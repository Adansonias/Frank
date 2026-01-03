class Broker:
    def __init__(
        self,
        starting_cash,
        name="portfolio",
        commission_per_trade=0.0,
        spread_pct=0.0005,     # 0.05%
        slippage_pct=0.0003   # 0.03%
    ):
        self.name = name
        self.cash = starting_cash
        self.starting_cash = starting_cash
        self.positions = {}  # ticker -> {shares, entry_price}
        self.realized_pnl = 0.0

        # Cost model
        self.commission = commission_per_trade
        self.spread_pct = spread_pct
        self.slippage_pct = slippage_pct

    # ------------------------------------
    # Internal price adjustment
    # ------------------------------------
    def _apply_costs(self, price, side):
        spread_cost = price * self.spread_pct / 2
        slippage_cost = price * self.slippage_pct

        if side == "BUY":
            return price + spread_cost + slippage_cost
        else:  # SELL
            return price - spread_cost - slippage_cost

    # ------------------------------------
    # BUY
    # ------------------------------------
    def buy(self, ticker, price, amount):
        price = self._apply_costs(price, "BUY")
        total_cost = amount + self.commission

        if total_cost > self.cash:
            return False

        shares = amount / price
        self.cash -= total_cost

        self.positions[ticker] = {
            "shares": shares,
            "entry_price": price
        }
        return True

    # ------------------------------------
    # SELL
    # ------------------------------------
    def sell(self, ticker, price):
        if ticker not in self.positions:
            return False

        price = self._apply_costs(price, "SELL")
        pos = self.positions.pop(ticker)

        proceeds = pos["shares"] * price - self.commission
        cost = pos["shares"] * pos["entry_price"]

        pnl = proceeds - cost
        self.realized_pnl += pnl
        self.cash += proceeds
        return pnl

    # ------------------------------------
    # PnL Helpers
    # ------------------------------------
    def unrealized_pnl(self, prices):
        pnl = 0.0
        for ticker, pos in self.positions.items():
            if ticker in prices:
                pnl += (prices[ticker] - pos["entry_price"]) * pos["shares"]
        return pnl

    def equity(self, prices):
        return self.cash + sum(
            pos["shares"] * prices.get(t, pos["entry_price"])
            for t, pos in self.positions.items()
        )
