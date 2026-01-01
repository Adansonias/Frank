# Frank

## Project Description

Frank :)

## Setting up the project

First create and activate a python virtual environment to manage package installations

```bash
# Change directory into the newly cloned repository
cd Frank
# Create the virtual environment in this directory
python -m venv .venv
# Next, source the virtual environment
source .venv/Scripts/activate
```

Once the virtual environment has been sourced, you can install all of the required packages from the `requirements.txt` file

```bash
# wowza, run this command for the holy texts needeed to run the stuffz
pip install -r requirements.txt
```

## To Run

The final step is to run the main.py script to start up the project

```bash
python src/main.py
```

## Running the charting script

To see the live updated state of the bot, run the `chart.py` script

```bash
python src/chart.py
```
