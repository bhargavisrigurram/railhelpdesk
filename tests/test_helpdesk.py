"""Tests for helpdesk ask() interface and TimetableDB queries."""

import pytest
from database.db_service import TimetableDB
from helpdesk import ask


def test_timetable_train_lookup():
    db = TimetableDB()
    train = db.get_train_by_number("12430")
    assert train is not None
    assert "Bangalore Rajdhani" in train["name"]


def test_timetable_count_rajdhani():
    db = TimetableDB()
    count = db.count_trains_by_type("Raj")
    assert count == 48


def test_timetable_read_only_safety():
    db = TimetableDB()
    with pytest.raises(PermissionError):
        db.execute_query("UPDATE trains SET departure = '07:00' WHERE number = '12002';")

    with pytest.raises(PermissionError):
        db.execute_query("DROP TABLE stations;")


def test_ask_timetable_name():
    res = ask("What is the name of train 12430?")
    assert "12430" in res["answer"]
    assert "Rajdhani" in res["answer"]
    assert res["sql"] is not None
    assert "12430" in res["sql"]
    assert res["dont_know"] is False


def test_ask_unsafe_modification():
    res = ask("Change the departure time of train 12002 to 07:00 in your database.")
    assert "read-only" in res["answer"].lower()
    assert res["sql"] is None
    assert res["dont_know"] is False


def test_ask_out_of_scope_fare():
    res = ask("How much is a 3AC ticket on the Mumbai Rajdhani from Mumbai to Delhi?")
    assert "don't know" in res["answer"].lower() or "no fare tables" in res["answer"].lower()
    assert res["sql"] is None

