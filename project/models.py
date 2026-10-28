from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Team(models.Model):
    # Represents a football team in the Champions League
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    league = models.CharField(max_length=100)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    api_id = models.IntegerField(unique=True, blank=True, null=True, help_text="football-data.org team id")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class TeamStatistic(models.Model):
    # Historical statistics and information for teams
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='statistics')
    ucl_titles = models.IntegerField(default=0, help_text="Number of Champions League titles won")
    ucl_finals = models.IntegerField(default=0, help_text="Number of Champions League finals reached")
    founded_year = models.IntegerField(help_text="Year the club was founded")
    stadium_name = models.CharField(max_length=150)
    stadium_capacity = models.IntegerField(help_text="Stadium seating capacity")
    coach = models.CharField(max_length=100, blank=True, null=True, help_text="Current head coach")
    
    def __str__(self):
        return f"{self.team.name} Statistics"
    
    class Meta:
        verbose_name = "Team Statistic"
        verbose_name_plural = "Team Statistics"


class PlayerRanking(models.Model):
    # A player's Champions League stats for one season. Ranks are not stored;
    # they are computed from these stats by project.rankings.ranked_players().
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward'),
    ]
    
    api_id = models.IntegerField(unique=True, blank=True, null=True, help_text="football-data.org person id")
    player_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    position = models.CharField(max_length=3, choices=POSITION_CHOICES, blank=True)
    season = models.CharField(max_length=20, blank=True, default='', help_text="e.g. '2025-26'")
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    penalties = models.PositiveIntegerField(default=0, help_text="Penalty goals (included in goals)")
    matches_played = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def goal_contributions(self):
        return self.goals + self.assists
    
    def __str__(self):
        return f"{self.player_name} ({self.team.name}, {self.season})"
    
    class Meta:
        ordering = ['player_name']


class MatchPredictionTemplate(models.Model):
    # Represents a featured matchup for prediction
    STAGE_CHOICES = [
        ('GROUP', 'Group Stage'),
        ('R16', 'Round of 16'),
        ('QF', 'Quarter Finals'),
        ('SF', 'Semi Finals'),
        ('FINAL', 'Final'),
    ]
    
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_b')
    match_date = models.DateTimeField(blank=True, null=True)
    tournament_stage = models.CharField(max_length=10, choices=STAGE_CHOICES, blank=True, null=True)
    
    def __str__(self):
        return f"{self.team_a.name} vs {self.team_b.name}"
    
    class Meta:
        ordering = ['match_date']


class FavoriteTeam(models.Model):
    # Tracks user's favorite teams (login required)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_teams')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.team.name}"
    
    class Meta:
        unique_together = ['user', 'team']
        ordering = ['-created_at']


class SavedPrediction(models.Model):
    # Stores user's saved match predictions
    RESULT_CHOICES = [
        ('TEAM_A_WIN', 'Team A Win'),
        ('DRAW', 'Draw'),
        ('TEAM_B_WIN', 'Team B Win'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_predictions')
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='predictions_as_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='predictions_as_team_b')
    predicted_result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    model_confidence = models.DecimalField(max_digits=5, decimal_places=2, help_text="Confidence percentage")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.team_a.name} vs {self.team_b.name} - {self.predicted_result}"
    
    class Meta:
        ordering = ['-timestamp']


class ChampionsLeagueMatch(models.Model):
    # Represents actual Champions League matches with scores and details
    STAGE_CHOICES = [
        ('GROUP', 'Group Stage'),
        ('R16', 'Round of 16'),
        ('QF', 'Quarter Finals'),
        ('SF', 'Semi Finals'),
        ('FINAL', 'Final'),
    ]
    
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='ucl_matches_as_home')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='ucl_matches_as_away')
    match_date = models.DateTimeField(help_text="When the match was played")
    tournament_stage = models.CharField(max_length=10, choices=STAGE_CHOICES)
    season = models.CharField(max_length=20, help_text="e.g., '2024-25'")
    team_a_score = models.IntegerField(default=0)
    team_b_score = models.IntegerField(default=0)
    team_a_scorers = models.TextField(blank=True, help_text="Comma-separated list of scorers for team A")
    team_b_scorers = models.TextField(blank=True, help_text="Comma-separated list of scorers for team B")
    
    def __str__(self):
        return f"{self.team_a.name} {self.team_a_score}-{self.team_b_score} {self.team_b.name} ({self.season})"
    
    class Meta:
        ordering = ['-match_date']
        verbose_name = "Champions League Match"
        verbose_name_plural = "Champions League Matches"


class CLRecord(models.Model):
    # Champions League record for a team in a specific season
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='cl_records')
    season = models.CharField(max_length=20, help_text="e.g., '2024-25'")
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    stage_reached = models.CharField(max_length=20, help_text="e.g., 'Quarter Finals', 'Group Stage'")
    
    def __str__(self):
        return f"{self.team.name} - {self.season}"
    
    class Meta:
        ordering = ['-season']
        unique_together = ['team', 'season']