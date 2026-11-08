import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

from pydantic import AwareDatetime, BaseModel, Field, ValidationError, ValidationInfo
from pydantic import field_validator, model_validator

NAME_MAX = 50
ERP_TZ = timezone(timedelta(hours=-5))  # every ISO date from this ERP comes with -05:00
STATUS = {"1": True, "Activo": True, "0": False, "Inactivo": False}


class ErpAsset(BaseModel):
    code: str = Field(min_length=1)
    name: str = Field(min_length=1)
    active: bool = Field(alias="status")
    cost: Decimal = Field(alias="acquisition_cost")
    location: str = Field(alias="parent_location")
    installed_at: AwareDatetime
    installed_at_tz_assumed: bool = False

    @field_validator("active", mode="before")
    @classmethod
    def _status(cls, v):
        if not isinstance(v, str) or v not in STATUS:
            raise ValueError(f"unknown value {v!r}")
        return STATUS[v]

    @field_validator("cost", mode="before")
    @classmethod
    def _latin_amount(cls, v):
        # Text amounts use "." for thousands and "," for decimals: "1.234,56".
        if isinstance(v, str):
            return v.replace(".", "").replace(",", ".")
        return v

    @field_validator("location")
    @classmethod
    def _in_catalog(cls, v, info: ValidationInfo):
        if v not in info.context["locations"]:
            raise ValueError(f"{v!r} not in catalog")
        return v

    @model_validator(mode="before")
    @classmethod
    def _date_without_timezone(cls, data):
        # "13/04/2026" is day/month/year: 13 and 16 can't be months.
        value = data.get("installed_at") if isinstance(data, dict) else None
        if isinstance(value, str) and "/" in value:
            try:
                day = datetime.strptime(value, "%d/%m/%Y")
            except ValueError:
                return data
            return {**data, "installed_at": day.replace(tzinfo=ERP_TZ),
                    "installed_at_tz_assumed": True}
        return data


class Reading(BaseModel):
    meter: str = Field(min_length=1)
    value: Decimal
    read_at: AwareDatetime


@dataclass(frozen=True)
class Asset:
    code: str
    name: str
    active: bool
    cost: Decimal
    location: str
    installed_at: datetime  # UTC
    readings: list[Reading]
    record_hash: str
    warnings: list[str]


def validate(raw: dict, locations: set[str]) -> tuple[ErpAsset | None, list[str]]:
    try:
        return ErpAsset.model_validate(raw, context={"locations": locations}), []
    except ValidationError as e:
        return None, [_reason(err) for err in e.errors()]


def latest_readings(raw: list[dict]) -> list[Reading]:
    latest = {}
    for reading in (Reading.model_validate(r) for r in raw):
        current = latest.get(reading.meter)
        if current is None or reading.read_at > current.read_at:
            latest[reading.meter] = reading
    return sorted(latest.values(), key=lambda r: r.meter)


def normalize(erp: ErpAsset, readings: list[Reading]) -> Asset:
    warnings = []
    name = erp.name
    if len(name) > NAME_MAX:
        warnings.append(f"name: truncated from {len(name)} to {NAME_MAX} chars")
        name = name[:NAME_MAX]
    if erp.installed_at_tz_assumed:
        warnings.append("installed_at: no timezone, assumed -05:00")

    cost = erp.cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    installed_at = erp.installed_at.astimezone(timezone.utc)
    readings = [r.model_copy(update={"read_at": r.read_at.astimezone(timezone.utc)})
                for r in readings]

    return Asset(
        code=erp.code,
        name=name,
        active=erp.active,
        cost=cost,
        location=erp.location,
        installed_at=installed_at,
        readings=readings,
        record_hash=_record_hash(erp.code, name, erp.active, cost, erp.location,
                                 installed_at, readings),
        warnings=warnings,
    )


def _record_hash(code, name, active, cost, location, installed_at, readings) -> str:
    # Not Python's hash(): it changes from one process to the next.
    content = {
        "code": code,
        "name": name,
        "active": active,
        "cost": str(cost),
        "location": location,
        "installed_at": installed_at.isoformat(),
        "readings": [
            {"meter": r.meter, "value": str(r.value), "read_at": r.read_at.isoformat()}
            for r in readings
        ],
    }
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _reason(err) -> str:
    field = ".".join(str(part) for part in err["loc"])
    if err["type"] == "missing" or err["input"] is None:
        return f"{field}: missing"
    if err["type"] == "value_error":
        return f"{field}: {err['ctx']['error']}"
    return f"{field}: {err['msg']}"
