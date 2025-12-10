from django.contrib import admin
from .models import Team, PlayerRanking, MatchPredictionTemplate, FavoriteTeam, SavedPrediction, TeamStatistic, ChampionsLeagueMatch, CLRecord

# Register your models here.

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'league']
    list_filter = ['country', 'league',]
    search_fields = ['name', 'country']

@admin.register(TeamStatistic)
class TeamStatisticAdmin(admin.ModelAdmin):
    list_display = ['team', 'ucl_titles', 'ucl_finals', 'founded_year', 'stadium_name', 'stadium_capacity']
    list_filter = ['ucl_titles', 'founded_year']
    search_fields = ['team__name', 'stadium_name']


@admin.register(PlayerRanking)
class PlayerRankingAdmin(admin.ModelAdmin):
    list_display = ['rank_int', 'player_name', 'team', 'position', 'ga_per_90']
    list_filter = ['position', 'team']
    search_fields = ['player_name']
    ordering = ['rank_int']


@admin.register(MatchPredictionTemplate)
class MatchPredictionTemplateAdmin(admin.ModelAdmin):
    list_display = ['team_a', 'team_b', 'tournament_stage', 'match_date']
    list_filter = ['tournament_stage', 'match_date']
    search_fields = ['team_a__name', 'team_b__name']


@admin.register(FavoriteTeam)
class FavoriteTeamAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'created_at']
    list_filter = ['team', 'created_at']
    search_fields = ['user__username', 'team__name']


@admin.register(SavedPrediction)
class SavedPredictionAdmin(admin.ModelAdmin):
    list_display = ['user', 'team_a', 'team_b', 'predicted_result', 'model_confidence', 'timestamp']
    list_filter = ['predicted_result', 'timestamp']
    search_fields = ['user__username', 'team_a__name', 'team_b__name']


@admin.register(ChampionsLeagueMatch)
class ChampionsLeagueMatchAdmin(admin.ModelAdmin):
    list_display = ['team_a', 'team_b', 'team_a_score', 'team_b_score', 'match_date', 'season', 'tournament_stage']
    list_filter = ['season', 'tournament_stage', 'match_date']
    search_fields = ['team_a__name', 'team_b__name']
    date_hierarchy = 'match_date'


@admin.register(CLRecord)
class CLRecordAdmin(admin.ModelAdmin):
    list_display = ['team', 'season', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'stage_reached']
    list_filter = ['season', 'stage_reached']
    search_fields = ['team__name', 'season']