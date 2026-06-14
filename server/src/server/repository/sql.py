import os
from dataclasses import dataclass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from server.repository.base import SurvivalGroupBy, SurvivalRate


@dataclass(frozen=True)
class SqlSettings:
    """Connection configuration for the SQL-backed repository."""

    database_url: str

    @classmethod
    def from_env(cls) -> "SqlSettings":
        """Read settings from the environment.

        Raises:
            RuntimeError: if ``TITANIC_DATABASE_URL`` is not set.
        """
        url = os.getenv("TITANIC_DATABASE_URL")
        if url is None:
            raise RuntimeError("TITANIC_DATABASE_URL is not set")
        return cls(database_url=url)


class SqlTitanicRepository:
    """:class:`TitanicRepository` backed by a SQL database via SQLAlchemy.

    Owns the engine (and its connection pool); call :meth:`dispose` to
    release it.
    """

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @classmethod
    def from_settings(cls, settings: SqlSettings) -> "SqlTitanicRepository":
        """Build from explicit settings."""
        return cls(create_engine(settings.database_url))

    @classmethod
    def from_env(cls) -> "SqlTitanicRepository":
        """Build from environment-derived settings (production default)."""
        return cls.from_settings(SqlSettings.from_env())

    def dispose(self) -> None:
        self._engine.dispose()

    def get_survival_rate(self, group_by: SurvivalGroupBy) -> list[SurvivalRate]:
        if group_by is SurvivalGroupBy.PASSENGER_CLASS:
            query = """
                SELECT c.class AS label, count(*) AS n, avg(o.survived) AS rate
                FROM Observation o
                JOIN Class c ON o.class_id = c.class_id
                GROUP BY c.class
                ORDER BY c.class_id
            """
        elif group_by is SurvivalGroupBy.SEX:
            query = """
                SELECT s.sex AS label, count(*) AS n, avg(o.survived) AS rate
                FROM Observation o
                JOIN Sex s ON o.sex_id = s.sex_id
                GROUP BY s.sex
                ORDER BY s.sex_id
            """
        else:
            # Unreachable while every enum member is mapped above; guards
            # against a newly added dimension silently returning nothing.
            raise ValueError(f"Unsupported group_by: {group_by!r}")

        with self._engine.connect() as conn:
            rows = conn.execute(text(query)).all()

        return [
            SurvivalRate(
                **{group_by.value: row.label},
                count=row.n,
                survival_rate=row.rate,
            )
            for row in rows
        ]
