# src/logic/team.py

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass()
class Team:
    id: int = field(
        metadata={
            "db_column": "team_id",
            "description": "Unique identifier for the team",
            "required": True,
            "type": "integer"
        }
    )
   
    name: str = field(default_factory=str,
        metadata={
            "db_column": "team_name",
            "description": "Name of the team",
            "required": True,
            "type": "string"
        }
        
    )

    logo_url: Optional[str] = field(default=None, 
        metadata={
            "db_column": "logo_url",
            "description": "URL of the team's logo",
            "required": False,
            "type": "string"
        }
    )

    series_wons: int = field(default=0,
        metadata={
            "db_column": "series_wons",
            "description": "Number of series won by the team",
            "required": True,
            "type": "integer"
        }
    )

    series_losts: int = field(default=0,
        metadata={
            "db_column": "series_losts",
            "description": "Number of series lost by the team",
            "required": True,
            "type": "integer"
        }
    )

    maps_won: int = field(default=0,
        metadata={
            "db_column": "maps_won",
            "description": "Number of maps won by the team",
            "required": True,
            "type": "integer"
        }
    )

    maps_lost: int = field(default=0,
        metadata={
            "db_column": "maps_lost",
            "description": "Number of maps lost by the team",
            "required": True,
            "type": "integer"
        }
    )

    quickest_map_win_time: Optional[float] = field(default=None,
        metadata={
            "db_column": "quickest_map_win_time",
            "description": "Quickest map win time in seconds",
            "required": False,
            "type": "float"
        }
    )
    
    series_ids: List[int] = field(default_factory=list,
        metadata={
            "db_column": "series_ids",
           "description": "List of series IDs the team has participated in",
           "relation": "many-to-many",
           "required": False,
           "type": "list of integers",
           "target-table": "series"
        }
    )

    def __post_init__(self):
        if self.series_wons < 0 or self.series_losts < 0 or self.maps_won < 0 or self.maps_lost < 0:
            raise ValueError("Win and loss counts cannot be negative.")

    def to_dict(self) -> dict:
        return {
            k: getattr(self, k) for k in self.__dataclass_fields__
        }
    
    @property
    def total_series_played(self) -> int:
        return self.series_wons + self.series_losts

    @property
    def total_maps_played(self) -> int:
        return self.maps_won + self.maps_lost
    
    @property
    def series_win_rate(self) -> float:
        total = self.total_series_played
        return (self.series_wons / total) * 100 if total > 0 else 0.0
    
    @property
    def maps_win_rate(self) -> float:
        total = self.total_maps_played
        return (self.maps_won / total) * 100 if total > 0 else 0.0


    def record_series_result(self, won:bool, maps_won:int, maps_lost:int, map_win_time:Optional[List[float]]=None):
        if won:
            self.series_wons += 1
        else:
            self.series_losts += 1
        
        self.maps_won += maps_won
        self.maps_lost += maps_lost

        if map_win_time is not None:
            for time in map_win_time:
                if self.quickest_map_win_time is None or time < self.quickest_map_win_time:
                    self.quickest_map_win_time = time


    def add_series(self, series_id:int):
        if series_id not in self.series_ids:
            self.series_ids.append(series_id)