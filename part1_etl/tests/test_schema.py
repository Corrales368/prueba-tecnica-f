from decimal import Decimal

import pytest

from etl.schema import latest_readings, normalize, validate

LOCATIONS = {"LOC-A", "LOC-B"}


def raw(**changes):
    record = {
        "code": "EQ-001",
        "name": "Equipo 001",
        "status": "1",
        "acquisition_cost": "1.234,56",
        "parent_location": "LOC-B",
        "installed_at": "2026-02-11T01:30:00-05:00",
        "updated_at": "2026-08-11T12:00:00-05:00",
    }
    return {**record, **changes}


def process(record, readings=()):
    erp, reasons = validate(record, LOCATIONS)
    assert reasons == []
    return normalize(erp, latest_readings(list(readings)))


@pytest.mark.parametrize("status, active", [
    ("1", True), ("Activo", True), ("0", False), ("Inactivo", False),
])
def test_status_becomes_active(status, active):
    assert process(raw(status=status)).active is active


@pytest.mark.parametrize("changes, reason", [
    ({"status": None}, "status: missing"),
    ({"status": "Si"}, "status: unknown value 'Si'"),
    ({"acquisition_cost": None}, "acquisition_cost: missing"),
    ({"parent_location": "LOC-Z"}, "parent_location: 'LOC-Z' not in catalog"),
    ({"code": None}, "code: missing"),
])
def test_rejection_reason(changes, reason):
    erp, reasons = validate(raw(**changes), LOCATIONS)
    assert erp is None
    assert reasons == [reason]


def test_missing_field_is_rejected():
    record = raw()
    del record["status"]
    assert validate(record, LOCATIONS) == (None, ["status: missing"])


@pytest.mark.parametrize("changes, field", [
    ({"acquisition_cost": "abc"}, "acquisition_cost"),
    ({"installed_at": "2026-02-11T01:30:00"}, "installed_at"),
    ({"installed_at": "31/02/2026"}, "installed_at"),
    ({"code": ""}, "code"),
])
def test_invalid_values_are_rejected(changes, field):
    erp, reasons = validate(raw(**changes), LOCATIONS)
    assert erp is None
    assert len(reasons) == 1 and reasons[0].startswith(f"{field}: ")


def test_every_reason_is_reported_at_once():
    _, reasons = validate(
        raw(status=None, acquisition_cost=None, parent_location="LOC-Z"), LOCATIONS
    )
    assert sorted(reasons) == [
        "acquisition_cost: missing",
        "parent_location: 'LOC-Z' not in catalog",
        "status: missing",
    ]


def test_keeps_only_the_latest_reading_of_each_meter():
    readings = [
        {"meter": "MED-02", "value": 1.0, "read_at": "2026-08-12T01:15:00-05:00"},
        {"meter": "MED-01", "value": 2.0, "read_at": "2026-08-13T01:15:00+00:00"},
        # Earlier as text, but later in time (04:15 UTC): must win.
        {"meter": "MED-01", "value": 3.0, "read_at": "2026-08-12T23:15:00-05:00"},
        {"meter": "MED-02", "value": 4.0, "read_at": "2026-08-14T01:15:00-05:00"},
    ]
    latest = latest_readings(readings)
    assert [(r.meter, r.value) for r in latest] == [
        ("MED-01", Decimal("3.0")),
        ("MED-02", Decimal("4.0")),
    ]


@pytest.mark.parametrize("cost, expected", [
    ("1.234,56", "1234.56"),
    ("12.500,00", "12500.00"),
    ("890,10", "890.10"),
    (1234.56, "1234.56"),
    (45000.0, "45000.00"),
])
def test_cost_has_two_decimals_whatever_the_format(cost, expected):
    assert str(process(raw(acquisition_cost=cost)).cost) == expected


def test_cost_rounds_half_up():
    assert str(process(raw(acquisition_cost="10,005")).cost) == "10.01"


def test_iso_date_is_converted_to_utc():
    asset = process(raw(installed_at="2026-02-11T01:30:00-05:00"))
    assert asset.installed_at.isoformat() == "2026-02-11T06:30:00+00:00"
    assert asset.warnings == []


def test_date_without_timezone_is_day_month_year_at_minus_five():
    asset = process(raw(installed_at="13/04/2026"))
    assert asset.installed_at.isoformat() == "2026-04-13T05:00:00+00:00"
    assert asset.warnings == ["installed_at: no timezone, assumed -05:00"]


def test_long_name_is_truncated_and_reported():
    asset = process(raw(name="x" * 84))
    assert asset.name == "x" * 50
    assert asset.warnings == ["name: truncated from 84 to 50 chars"]


def test_hash_has_a_fixed_value():
    # If this value changes, every stored asset looks "updated" on the next run.
    assert process(raw()).record_hash == (
        "d8faff70847a08ea790fb58079f7390d2b2b44a928b01a9998b213ea72a1d4c4"
    )


def test_hash_ignores_updated_at_and_status_spelling():
    before = process(raw(status="Inactivo", updated_at="2026-08-13T12:00:00-05:00"))
    after = process(raw(status="0", updated_at="2026-08-24T09:00:00-05:00"))
    assert before.record_hash == after.record_hash


def test_hash_changes_when_content_changes():
    reading = {"meter": "MED-01", "value": 1.0, "read_at": "2026-08-12T01:15:00-05:00"}
    base = process(raw()).record_hash
    assert process(raw(acquisition_cost="1.234,57")).record_hash != base
    assert process(raw(), [reading]).record_hash != base
