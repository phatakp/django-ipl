from django.contrib import admin
from .models import Team, Match, Static, Bet


@admin.register(Static)
class StaticAdmin(admin.ModelAdmin):
    list_display = ("row", "bet_choices", "team_chg_amt")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "logo", "back_color", "fore_color")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("num", "date", "home_team", "away_team", "typ", "min_bet",
                    "venue", "status", "winner", "home_win_pct", "away_win_pct")
    list_filter = ("home_team", "away_team",
                   "venue", "winner")


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ("player", "match", "bet_team", "bet_amt",
                    "win_amt", "lost_amt", "status", "create_time")
    list_filter = ("player", "match", "bet_team",
                   "status")
