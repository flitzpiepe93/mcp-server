from server.repository.base import SurvivalGroupBy, SurvivalRate


class MemoryTitanicRepository:
    """In-memory :class:`TitanicRepository` for tests.

    Returns the canned results it is constructed with, so tests stay fast and
    deterministic without a real database. It is a test double, not a second
    aggregation engine: it does not compute figures from raw observations.
    """

    def __init__(self, results: dict[SurvivalGroupBy, list[SurvivalRate]]) -> None:
        self._results = results

    def get_survival_rate(self, group_by: SurvivalGroupBy) -> list[SurvivalRate]:
        if group_by not in self._results:
            raise ValueError(f"Unsupported group_by: {group_by!r}")
        return self._results[group_by]

    def dispose(self) -> None:
        pass
