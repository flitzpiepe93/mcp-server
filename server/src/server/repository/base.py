from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, field_validator


class SurvivalGroupBy(StrEnum):
    """Dimension to aggregate survival figures by.

    A ``StrEnum`` so the wire value sent by an agent (plain JSON string)
    maps directly onto a member, and FastMCP advertises the allowed values
    in the tool schema.
    """

    PASSENGER_CLASS = "passenger_class"
    SEX = "sex"


class SurvivalRate(BaseModel):
    """Survival figures for a single group.

    Only the field matching the requested :class:`SurvivalGroupBy` is set;
    the others stay ``None``.
    """

    passenger_class: str | None = None
    sex: str | None = None
    count: int
    survival_rate: float

    @field_validator("survival_rate")
    @classmethod
    def _round_rate(cls, value: float) -> float:
        """Survival rate is reported to three decimal places, regardless of
        which repository computed it."""
        return round(value, 3)


class TitanicRepository(Protocol):
    """Domain interface over the Titanic dataset.

    The server depends only on this protocol, never on a concrete database.
    Implementations are swappable (SQL, in-memory) without touching server
    code.
    """

    def get_survival_rate(self, group_by: SurvivalGroupBy) -> list[SurvivalRate]:
        """Return survival figures aggregated by the given dimension."""
        ...

    def dispose(self) -> None:
        """Release implementation-owned resources (e.g. a connection pool).

        Part of the interface so the server can tear any implementation down
        uniformly; implementations without resources (in-memory) no-op.
        """
        ...
