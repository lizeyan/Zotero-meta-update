from dataclasses import dataclass
from typing import Optional

from work.work import Work


@dataclass
class ConferencePaper(Work):
    conference_name: Optional[str] = None
    proceeding_name: Optional[str] = None
    location: Optional[str] = None
    series: Optional[str] = None
