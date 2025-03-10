"""
Script Name: all_variable.py
Author: Sushen Biswas
Date: 2023-03-26
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Variable:
    BIG_DATABASE = r"../database/big_crypto_4years.db"
    SMALL_DATABASE = r"../database_small/small_crypto.db"
    AI_DATABASE = r"../database_ai/small_crypto.db"
    STATIC_DAY = 2
    CANDLE_PATTERN_LOGBACK = "5"
    DOLLAR = 22
    STOP_LOSS = .025
    DAYS_YOU_RUN_THE_PROGRAM = 90
    CHANGE_STOP_LOSS_WHEN_BUYING_PRICE_CHANGE = 0.25
    STOP_LOSS_QTY = 2
    BUYING_STOP_LOSS = .005
    MAIL = os.environ.get('GMAIL')