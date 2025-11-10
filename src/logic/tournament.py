# src/logic/tournnament.py

from dataclasses import dataclass, field
from typing import List, Optional
from .team import Team
from .match import Match
from .swiss import Swiss
from .playoffs import Playoffs
import math

@dataclass
class Tournament:
    name: str
    teams: List[Team]
    swiss: Optional[Swiss] = None
    playoffs: Optional[Playoffs] = None
    champion: Optional[Team] = None
    phase: str = field(default= "swiss")  # "swiss" or "playoffs"
    total_swiss_rounds: int = field(init=False)

    def __post_init__(self):
        from database.db_manager import DatabaseManager

        self.db = DatabaseManager("tournament.db")
        self.db.init_db("src/database/schema.sql")

        self.tournament_id = self.db.insert_tournament(self.name)
        for team in self.teams:
            team.id = self.db.insert_team(team.name, team.image_path)

        if len(self.teams) < 8:
            raise ValueError("A tournament must have at least 8 teams.")

        # Calcular automáticamente número de rondas suizas
        self.total_swiss_rounds = self.calculate_swiss_rounds(len(self.teams))

        print(f"Tournament '{self.name}' initialized with {len(self.teams)} teams.")
        self.start_swiss_phase()
    
    def calculate_swiss_rounds(self, n_teams: int) -> int:
        rounds = math.ceil(math.log2(n_teams / 8)) + 3
        return max(rounds, 3)
        
    def start_swiss_phase(self):
        self.swiss = Swiss(teams=self.teams)
        self.phase = "swiss"
        self.swiss.start_next_round()
        print("Swiss phase started.")
    
    def report_match_result(self, match: Match, winner: Team, team1_maps_won: int, team2_maps_won: int, team1_win_time: Optional[float] = None, team2_win_time: Optional[float] = None):
        if self.phase == "swiss" and self.swiss:
            self.swiss.record_match_result(match, winner, team1_maps_won, team2_maps_won, team1_win_time, team2_win_time)
        elif self.phase == "playoffs" and self.playoffs:
            self.playoffs.record_match_result(match, team1_maps_won, team2_maps_won, team1_win_time, team2_win_time)
        else:
            raise ValueError("No active phase to report match results.")
        self.db.insert_match_result(
            tournament_id=self.tournament_id,
            team1_id=match.team1.id,
            team2_id=match.team2.id if match.team2 else None,
            winner_id=winner.id,
            team1_maps_won=team1_maps_won,
            team2_maps_won=team2_maps_won,
            team1_win_time=team1_win_time,
            team2_win_time=team2_win_time,
            round_number=self.swiss.current_round if self.phase == "swiss" else self.playoffs.current_round
        )
        self.db.update_team_stats(match.team1.id, match.team1.series_won, match.team1.series_lost, match.team1.maps_won, match.team1.maps_lost)
        if match.team2:
            self.db.update_team_stats(match.team2.id, match.team2.series_won, match.team2.series_lost, match.team2.maps_won, match.team2.maps_lost)
        
    
    def advance_swiss_round(self):
        if not self.swiss:
            raise ValueError("Swiss phase has not been started.")
        if self.swiss.is_swiss_completed():
            self.start_playoffs_phase()
            print("Swiss phase completed. Playoffs phase started.")
        else:
            self.swiss.start_next_round()
            print(f"Advanced to round {self.swiss.current_round} in Swiss phase.")

    def start_playoffs_phase(self):
        if not  self.swiss:
            raise ValueError("Swiss phase must be completed before starting playoffs.")
        qualifiers = self.swiss.get_qualifiers()
        for team in qualifiers:
            print(f"Qualified for Playoffs: {team.name}")
        
        self.phase = "playoffs"
        self.playoffs = Playoffs(teams=qualifiers)
        self.db.update_tournament_phase(self.tournament_id, "playoffs")

        
    def check_tournament_completion(self):
        if self.phase == "playoffs" and self.playoffs and self.playoffs.is_playoffs_completed():
            self.champion = self.playoffs.winner
            print(f"Tournament Champion: {self.champion.name}")
            self.db.set_champion(self.tournament_id, self.champion.id)
            return True
        return False
    
    def print_standings(self):
        if self.phase == "swiss" and self.swiss:
            self.swiss.print_standings()
        elif self.phase == "playoffs" and self.playoffs:
            self.playoffs.print_bracket()
        else:
            print("No active phase to display standings.")

    def get_champion(self) -> Optional[Team]:
        return self.champion
    
    def get_current_phase(self) -> str:
        return self.phase

    def print_status(self):
        print(f"Tournament: {self.name}")
        print(f"Current Phase: {self.phase}")
        if self.champion:
            print(f"Champion: {self.champion.name}")
        else:
            print("Champion: TBD")
        self.print_standings()
