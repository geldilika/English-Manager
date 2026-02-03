import pandas as pd
import requests
from io import StringIO
import numpy as np

from src.db import premier_league
from src.models.schema import Team, Player

RAW_BASE = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master"

def read_csv(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status
    return pd.read_csv(StringIO(r.text))

