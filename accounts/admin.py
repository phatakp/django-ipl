from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("user", "team", "staff","curr_amt", "bets_won","bets_lost")
