from django.db.models.aggregates import Count
from django.shortcuts import render, redirect
from django.apps import apps
from django.contrib.auth.decorators import login_required
from .calculations import get_win_pct
from .models import MatchHistory, AllStats, HomeStats, AwayStats, NeutralStats
from django.conf import settings
from django.db.models import Count, F
from django.utils import timezone
import math

Player = apps.get_model('accounts', 'Player')
Team = apps.get_model('ipl_app', 'Team')
Match = apps.get_model('ipl_app', 'Match')
Bet = apps.get_model('ipl_app', 'Bet')
Static = apps.get_model('ipl_app', 'Static')
teams = Team.objects.prefetch_related('home_hist', 'away_hist').all()

venues = {'CSK': 'Chennai', 'DC': 'Delhi', 'KXIP': 'Punjab', 'KKR': 'Kolkata',
          'RR': 'Rajasthan', 'RCB': 'Bangalore', 'MI': 'Mumbai', 'SRH': 'Hyderabad'}


def isWithinTime(match):
    return timezone.localtime().date() < match.date or \
        (timezone.localtime().date() == match.date and timezone.localtime().hour < 12)


def isStaffUser(user):
    obj = Player.objects.get(user=user)
    return obj.staff


@login_required
def upload_match(request):

    if isStaffUser(request.user):
        # Clear the Match Table
        Match.objects.all().delete()

        import csv
        import os
        path = os.path.join(settings.BASE_DIR, 'matches.csv')

        with open(path) as csvfile:
            data = csv.DictReader(csvfile)
            for i, record in enumerate(data):
                t1 = record['Team1']
                t2 = record['Team2']
                dt = record['Date']
                num = i + 1
                home_team = teams.get(name=t1)
                away_team = teams.get(name=t2)
                venue = 'Neutral'

                home_win_pct, away_win_pct = get_win_pct(
                    venue, home_team, away_team)

                if num < 29:
                    min_bet = 20
                else:
                    min_bet = 30

                Match.objects.create(num=num,
                                     date=dt,
                                     home_team=home_team,
                                     away_team=away_team,
                                     venue=venue,
                                     min_bet=min_bet,
                                     home_win_pct=home_win_pct,
                                     away_win_pct=away_win_pct
                                     )
        context = {'staff_message': 'Matches Uploaded'}
    else:
        context = {'staff_message': 'Not Authorized'}

    context['curr_player'] = Player.objects.filter(user=request.user)

    return render(request, 'ipl_app/dashboard.html', context)


@login_required
def default_bets(request=None, id=None):
    context = dict()
    if id is None:
        if isStaffUser(request.user):
            matches = Match.objects.filter(
                date__lte=timezone.localtime().date(), status='N')

            for match in matches:
                if not isWithinTime(match):
                    for player in Player.objects.all():
                        if not Bet.objects.filter(player=player, match=match).exists():
                            Bet.objects.create(player=player,
                                               match=match,
                                               bet_amt=match.min_bet
                                               )
            context['staff_message'] = 'Default Bets Uploaded'
        else:
            context = {'staff_message': 'Not Authorized'}
    else:
        match = Match.objects.get(id=id)
        if not isWithinTime(match):
            for player in Player.objects.all():
                if not Bet.objects.filter(player=player, match=match).exists():
                    Bet.objects.create(player=player,
                                       match=match,
                                       bet_amt=match.min_bet
                                       )
            context['staff_message'] = 'Default Bets Uploaded'
        else:
            context['staff_message'] = 'Threshold not passed yet'

    context['curr_player'] = Player.objects.filter(user=request.user)
    return render(request, 'ipl_app/dashboard.html', context)


@login_required
def upload_history(request):

    if isStaffUser(request.user):
        # Clear the Match History Table
        MatchHistory.objects.all().delete()

        import csv
        import os
        from django.utils.dateparse import parse_date
        path = os.path.join(settings.BASE_DIR, 'stats.csv')

        with open(path) as csvfile:
            data = csv.DictReader(csvfile)
            for record in data:
                t1 = record['Team1']
                t2 = record['Team2']
                dt = record['Date']
                ven = record['Venue']
                win_team = record['Result']

                team1 = teams.get(name=t1)
                team2 = teams.get(name=t2)
                venue = venues.get(ven, 'Neutral')
                if 'No Result' in win_team:
                    winner = None
                else:
                    winner = teams.get(name=win_team)

                date_str = f"{dt.split('/')[2]}-{dt.split('/')[0]}-{dt.split('/')[1]}"
                date = parse_date(date_str)

                MatchHistory.objects.create(date=date,
                                            team1=team1,
                                            team2=team2,
                                            venue=venue,
                                            winner=winner
                                            )

                # Create Reverse Record for easy stat generation
                MatchHistory.objects.create(date=date,
                                            team1=team2,
                                            team2=team1,
                                            venue=venue,
                                            winner=winner
                                            )

        context = {'staff_message': 'Match History Uploaded'}

    else:
        context = {'staff_message': 'Not Authorized'}

    context['curr_player'] = Player.objects.filter(user=request.user)
    return render(request, 'ipl_app/dashboard.html', context)


def insert_all_stats(team1=None, team2=None, matches=None):
    match_count = matches.count()
    match_wins = matches.filter(winner=team1).count()
    match_nr = matches.filter(winner__isnull=True).count()
    match_loss = match_count - match_wins - match_nr
    win_pct = math.floor(match_wins / (match_count-match_nr)
                         * 100) if match_count > match_nr else 0

    obj, created = AllStats.objects.update_or_create(team1=team1,
                                                     team2=team2,
                                                     defaults={'matches': match_count,
                                                               'wins': match_wins,
                                                               'loss': match_loss,
                                                               'no_result': match_nr,
                                                               'win_pct': win_pct})


def insert_home_stats(team1=None, team2=None, matches=None):
    home_count = matches.filter(venue=venues[team1.name]).count()
    home_wins = matches.filter(venue=venues[team1.name],
                               winner=team1).count()
    home_nr = matches.filter(venue=venues[team1.name],
                             winner__isnull=True).count()
    home_loss = home_count - home_wins - home_nr
    home_win_pct = math.floor(
        home_wins / (home_count-home_nr) * 100) if home_count > home_nr else 0

    obj, created = HomeStats.objects.update_or_create(team1=team1,
                                                      team2=team2,
                                                      defaults={'matches': home_count,
                                                                'wins': home_wins,
                                                                'loss': home_loss,
                                                                'no_result': home_nr,
                                                                'win_pct': home_win_pct})


def insert_neutral_stats(team1=None, team2=None, matches=None):
    neutral_count = matches.filter(venue='Neutral').count()
    neutral_wins = matches.filter(venue='Neutral',
                                  winner=team1).count()
    neutral_nr = matches.filter(venue='Neutral',
                                winner__isnull=True).count()
    neutral_loss = neutral_count - neutral_wins - neutral_nr
    neutral_win_pct = math.floor(
        neutral_wins / (neutral_count-neutral_nr) * 100) if neutral_count > neutral_nr else 0

    obj, created = NeutralStats.objects.update_or_create(team1=team1,
                                                         team2=team2,
                                                         defaults={'matches': neutral_count,
                                                                   'wins': neutral_wins,
                                                                   'loss': neutral_loss,
                                                                   'no_result': neutral_nr,
                                                                   'win_pct': neutral_win_pct})


def insert_away_stats(team1=None, team2=None):
    all_stats = AllStats.objects.get(team1=team1, team2=team2)
    home_stats = HomeStats.objects.get(team1=team1, team2=team2)
    neutral_stats = NeutralStats.objects.get(team1=team1, team2=team2)
    away_count = all_stats.matches - home_stats.matches - neutral_stats.matches
    away_wins = all_stats.wins - home_stats.wins - neutral_stats.wins
    away_nr = all_stats.no_result - home_stats.no_result - neutral_stats.no_result
    away_loss = away_count - away_wins - away_nr

    away_win_pct = math.floor(
        away_wins / (away_count-away_nr)*100) if away_count > away_nr else 0

    obj, created = AwayStats.objects.update_or_create(team1=team1,
                                                      team2=team2,
                                                      defaults={'matches': away_count,
                                                                'wins': away_wins,
                                                                'loss': away_loss,
                                                                'no_result': away_nr,
                                                                'win_pct': away_win_pct})


@login_required
def generate_team_stats(request):

    match_history = MatchHistory.objects.select_related("team1", "team2").all()

    # Clear all tables
    AllStats.objects.all().delete()
    HomeStats.objects.all().delete()
    AwayStats.objects.all().delete()
    NeutralStats.objects.all().delete()

    for team in teams:
        team_matches = match_history.filter(team1=team)

        # All Matches
        insert_all_stats(team1=team, matches=team_matches)

        # Home Matches
        insert_home_stats(team1=team, matches=team_matches)

        # Neutral Matches
        insert_neutral_stats(team1=team, matches=team_matches)

        # Away Matches
        insert_away_stats(team1=team)

        for oppn in teams:
            if team != oppn:
                vs_matches = team_matches.filter(team2=oppn)

                # All Matches
                insert_all_stats(team1=team,
                                 team2=oppn,
                                 matches=vs_matches)

                # Home Matches
                insert_home_stats(team1=team,
                                  team2=oppn,
                                  matches=vs_matches)

                # Neutral Matches
                insert_neutral_stats(team1=team,
                                     team2=oppn,
                                     matches=vs_matches)

                # Away Matches
                insert_away_stats(team1=team, team2=oppn)

    return redirect('iplapp:dashboard')
