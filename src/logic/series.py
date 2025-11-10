# src/logic/series.py

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Map:
    map_id:int
    winner_team_id: int
    win_time: float

    def to_dict(self) -> dict:
        return {
            "map_id": self.map_id,
            "winner_team_id": self.winner_team_id,
            "win_time": self.win_time
        }

@dataclass
class Series:
    id: int = field(
        metadata={
            "db_column": "series_id",
            "description": "Unique identifier for the series",
            "required": True,
            "type": "integer"
        }
    )

    team_a_id: int = field(
        metadata={
            "db_column": "team_a_id",
            "description": "Unique identifier for Team A",
            "required": True,
            "type": "integer"
        }
    )

    team_b_id: int = field(
        metadata={
            "db_column": "team_b_id",
            "description": "Unique identifier for Team B",
            "required": True,
            "type": "integer"
        }
    )

    winner_team_id: Optional[int] = field(default=None,
        metadata={
            "db_column": "winner_team_id",
            "description": "Unique identifier for the winning team",
            "required": False,
            "type": "integer"
        }
    )

    best_of: int = field(default=3,
        metadata={
            "db_column": "best_of",
            "description": "Number of maps in the series (e.g., best of 3)",
            "required": True,
            "type": "integer"
        }
    )

    map_results: List[Map] = field(default_factory=list,
        metadata={
            "db_column": "map_results",
            "description": "List of map results including winner and win time",
            "required": False,
            "type": "list of Map Objects"
        }
    )

    def add_map_result(self, map_id: int, winner_team_id: int, win_time: float):
        map_result = Map(map_id=map_id, winner_team_id= winner_team_id, win_time= win_time)
        if map_result not in self.map_results:
            self.map_results.append(map_result)

    def get_team_map_wins(self, team_id: int)-> List[Map]:
        return[result for result in self.map_results if result.winner_team_id == team_id] 

    def get_team_win_times(self, team_id: int)-> List[float]:
        return[result.win_time for result in self.map_results if result.winner_team_id == team_id]
    
    @property
    def get_team_maps_won_count(self, team_id: int)->int:
        return len(self.get_team_map_wins(team_id))
    
    @property
    def get_team_maps_lost_count(self, team_id:int)-> int:
        return len([result for result in self.map_results if result.winner_team_id != team_id])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "team_a_id": self.team_a_id,
            "team_b_id": self.team_b_id,
            "winner_team_id": self.winner_team_id,
            "best_of": self.best_of,
            "map_results": [r.to_dict() for r in self.map_results]
        }

