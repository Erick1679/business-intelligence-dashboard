"""Automated tests for the business intelligence dashboard."""

from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "app.py"
DATA_PATH = ROOT / "data/customer_transactions.csv"


def test_dataset_exists():
    assert DATA_PATH.is_file()


def test_dataset_quality():
    data = pd.read_csv(DATA_PATH)

    assert len(data) == 31

    counts = data["data_quality_status"].value_counts()

    assert counts["Valid"] == 26
    assert counts["Duplicate"] == 1
    assert counts["Needs Review"] == 4


def test_dashboard_loads_correct_kpis():
    app = AppTest.from_file(
        APP_PATH,
        default_timeout=20,
    ).run()

    assert not app.exception
    assert app.metric[0].value == "25,180.00"
    assert app.metric[1].value == "26"
    assert app.metric[2].value == "10"
    assert app.metric[3].value == "70.0%"
    assert app.metric[4].value == "968.46"


def test_country_filter():
    app = AppTest.from_file(
        APP_PATH,
        default_timeout=20,
    ).run()

    app.sidebar.multiselect[0].set_value(
        ["Uganda"]
    ).run()

    assert not app.exception
    assert app.metric[0].value == "1,840.00"
    assert app.metric[1].value == "4"
    assert app.metric[2].value == "1"


def test_empty_country_filter():
    app = AppTest.from_file(
        APP_PATH,
        default_timeout=20,
    ).run()

    app.sidebar.multiselect[0].set_value([]).run()

    assert not app.exception
    assert len(app.warning) > 0
