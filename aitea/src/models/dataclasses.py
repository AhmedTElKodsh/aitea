from dataclasses import dataclass, field
from enums import TeamType
from datetime import date

@dataclass
class TrackedTimeEntry:
    """A record of actual time spent on a feature."""
    id: str
    member_name: str
    tracked_time_hours: float
    process: str
    date: date
    team: TeamType

entry = TrackedTimeEntry(
    id="track_001",
    team=TeamType.BACKEND,
    member_name="BE-1",
    feature="CRUD",
    tracked_time_hours=4.5,
    process="Data Operations",
    date=date(2025, 1, 15)
)
print(entry)