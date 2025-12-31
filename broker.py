# broker.py

class Broker:
    def __init__(self, starting_cash, name="portfolio"):
        self.name = name
        self.cash = starting_cash
        self.positions = {}  # ticker -> {shares, entry_price}
        self.realized_pnl = 0.0

    def buy(self, ticker, price, amount):
        if amount > self.cash:
            return False

        shares = amount / price
        self.cash -= amount

        self.positions[ticker] = {
            "shares": shares,
            "entry_price": price
        }
        return True

    def sell(self, ticker, price):
        if ticker not in self.positions:
            return False

        pos = self.positions.pop(ticker)
        proceeds = pos["shares"] * price
        cost = pos["shares"] * pos["entry_price"]

        pnl = proceeds - cost
        self.realized_pnl += pnl
        self.cash += proceeds
        return pnl

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
