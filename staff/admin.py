from django.contrib import admin
from .models import MatchHistory, AllStats, HomeStats, AwayStats, NeutralStats


@admin.register(MatchHistory)
class MatchHistoryAdmin(admin.ModelAdmin):
    list_display = ("date", "team1", "team2",
                    "venue", "winner")
    list_filter = ("team1", "team2",
                   "venue", "winner")


@admin.register(AllStats)
class AllStatsAdmin(admin.ModelAdmin):
    list_display = ("team1", "team2", "matches", "wins",
                    "loss", "no_result", "win_pct")
    list_filter = ("team1", "team2")


@admin.register(HomeStats)
class HomeStatsAdmin(admin.ModelAdmin):
    list_display = ("team1", "team2", "matches", "wins",
                    "loss", "no_result", "win_pct")
    list_filter = ("team1", "team2")


@admin.register(AwayStats)
class AwayStatsAdmin(admin.ModelAdmin):
    list_display = ("team1", "team2", "matches", "wins",
                    "loss", "no_result", "win_pct")
    list_filter = ("team1", "team2")


@admin.register(NeutralStats)
class NeutralStatsAdmin(admin.ModelAdmin):
    list_display = ("team1", "team2", "matches", "wins",
                    "loss", "no_result", "win_pct")
    list_filter = ("team1", "team2")
