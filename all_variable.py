"""
Script Name: all_variable.py
Author: Sushen Biswas
Date: 2023-03-26
"""

import sys
import os

from resource_path import resource_path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _resolve_database_path() -> str:
    env_path = os.getenv("TRADINGAI_DB_PATH")
    if env_path:
        return env_path

    candidates = [
        os.path.join("data", "1_years_btc_crypto_data.db"),
        os.path.join("data", "crypto.db"),
        "1_years_btc_crypto_data.db",
        "crypto.db",
        os.path.join("database", "1_years_btc_crypto_data.db"),
        os.path.join("database", "crypto.db"),
    ]

    for rel_path in candidates:
        candidate = resource_path(rel_path)
        if os.path.isfile(candidate):
            return candidate

    appdata = os.getenv("APPDATA")
    if appdata:
        base_dir = os.path.join(appdata, "TradingAi")
    else:
        base_dir = os.path.join(os.getcwd(), "data")

    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "crypto.db")


class Variable:
    DATABASE = _resolve_database_path()
    ENTRY_SIGNAL = 1600
    LAVARAGE = 4
    STATIC_DAY = 2
    CANDLE_PATTERN_LOGBACK = "5"
    DOLLAR = 22
    STOP_LOSS = .025
    DAYS_YOU_RUN_THE_PROGRAM = 90
    CHANGE_STOP_LOSS_WHEN_BUYING_PRICE_CHANGE = 0.25
    STOP_LOSS_QTY = 2
    BUYING_STOP_LOSS = .005
    MAIL = os.environ.get('GMAIL')
    DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
