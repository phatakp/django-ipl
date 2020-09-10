from .models import Bet, Match
from django.apps import apps
from django.utils import timezone
from django.db.models import Sum, F
from .calculations import get_win_pct
import math

Player = apps.get_model('accounts', 'Player')
MatchHistory = apps.get_model('staff', 'MatchHistory')
AllStats = apps.get_model('staff', 'AllStats')
HomeStats = apps.get_model('staff', 'HomeStats')
AwayStats = apps.get_model('staff', 'AwayStats')
NeutralStats = apps.get_model('staff', 'NeutralStats')

venues = {'CSK': 'Chennai', 'DC': 'Delhi', 'KXIP': 'Punjab', 'KKR': 'Kolkata',
          'RR': 'Rajasthan', 'RCB': 'Bangalore', 'MI': 'Mumbai', 'SRH': 'Hyderabad'}


def isWithinTime(match):
    # return timezone.localtime().date() < match.date or \
    #     (timezone.localtime().date() == match.date and timezone.localtime().hour < 12)
    return True


def validate_and_save(player, match, team, bet_amt):
    print(bet_amt)
    if isWithinTime(match):
        if bet_amt.isnumeric():
            if Bet.objects.filter(player=player, match=match).exists():
                bet = Bet.objects.get(player=player, match=match)
                if bet.bet_team != team or \
                        bet.bet_amt >= int(bet_amt):
                    return f'Rs.{bet.bet_amt} already bet for {bet.bet_team.name}. Can only increase amount', False
                else:
                    Bet.objects.filter(id=bet.id).update(bet_amt=int(bet_amt),
                                                         status='P',
                                                         create_time=timezone.localtime())
                    # bet.bet_amt = int(bet_amt)
                    # bet.status = 'P'
                    # bet.create_time = timezone.localtime()
                    # bet.save()
                    return f"Bet increased to Rs.{bet_amt} for {team.name}", True

            elif int(bet_amt) >= match.min_bet:
                Bet.objects.create(player=player,
                                   match=match,
                                   bet_team=team,
                                   bet_amt=int(bet_amt),
                                   status='P')
                return f"Bet Placed - Rs.{bet_amt} for {team.name}", True
            else:
                return f"Minimum Bet is Rs.{match.min_bet}", False
        else:
            return f"Bet Amount should be number only", False
    else:
        return f"Past 12PM IST. Cannot modify for {str(match)}", False


def winning_bet(bet, amt):
    Bet.objects.filter(id=bet.id).update(win_amt=amt, status='W')
    Player.objects.filter(id=bet.player.id).update(curr_amt=F('curr_amt')+amt,
                                                   bets_won=F('bets_won')+1)


def losing_bet(bet, amt):
    Bet.objects.filter(id=bet.id).update(lost_amt=amt, status='L')
    Player.objects.filter(id=bet.player.id).update(curr_amt=F('curr_amt')-amt,
                                                   bets_lost=F('bets_lost')+1)


def valid_bets(plyr_cnt, match):
    return Bet.objects.filter(match=match).count() == plyr_cnt


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


def generate_team_stats(match):
    match_history = MatchHistory.objects.select_related("team1", "team2").all()
    for team in (match.home_team, match.away_team):
        team_matches = match_history.filter(
            team1=team)
        # All Matches
        insert_all_stats(team1=team, matches=team_matches)

        # Home Matches
        insert_home_stats(team1=team, matches=team_matches)

        # Neutral Matches
        insert_neutral_stats(team1=team, matches=team_matches)

        # Away Matches
        insert_away_stats(team1=team)

        for oppn in (match.home_team, match.away_team):
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


def save_to_history(match, win_team=None):
    MatchHistory.objects.create(date=match.date,
                                team1=match.home_team,
                                team2=match.away_team,
                                venue=match.venue,
                                winner=win_team)

    # Reverse record for stats
    MatchHistory.objects.create(date=match.date,
                                team1=match.away_team,
                                team2=match.home_team,
                                venue=match.venue,
                                winner=win_team)

    generate_team_stats(match)


def set_abandoned(match):

    save_to_history(match)
    home_win_pct, away_win_pct = get_win_pct(match.venue,
                                             match.home_team,
                                             match.away_team)
    Match.objects.filter(id=match.id).update(status='A',
                                             home_win_pct=home_win_pct,
                                             away_win_pct=away_win_pct)


def set_completed(match, win_team):
    save_to_history(match, win_team)
    home_win_pct, away_win_pct = get_win_pct(match.venue,
                                             match.home_team,
                                             match.away_team)
    Match.objects.filter(id=match.id).update(winner=win_team,
                                             status='P',
                                             home_win_pct=home_win_pct,
                                             away_win_pct=away_win_pct)


def get_totals(bet_teams, win_team):
    if win_team is None:
        td = 0
        tl = bet_teams.get(None, 0)
        tw = sum([bet_teams[k]
                  for k in set(list(bet_teams.keys())) - set([None])])
    else:
        td = bet_teams.get(None, 0)
        tw = bet_teams.get(win_team.id, 0)
        tl = sum([bet_teams[k]
                  for k in set(list(bet_teams.keys())) - set([win_team.id])])

    return tl, tw, td


def get_team_totals(match_bets):
    # Organize the bet totals by bet_team
    team_bet_totals = match_bets.values('bet_team').order_by(
        'bet_team').annotate(tot_bet=Sum('bet_amt'))
    bet_teams = dict()
    for bet in team_bet_totals:
        bet_teams[bet['bet_team']] = bet['tot_bet']
    return bet_teams


def settle_bets(match, win_team=None):
    match_bets = Bet.objects.filter(match=match)

    bet_teams = get_team_totals(match_bets)

    # Update bet wins and losses
    if win_team is None:    # Match Abandoned
        set_abandoned(match)
        total_lost, total_win, _ = get_totals(bet_teams, win_team)

        if total_lost > 0:    # Default bets were present
            for bet in match_bets.exclude(status='D'):
                if total_win > 0:
                    amt = bet.bet_amt / total_win * total_lost
                    winning_bet(bet, amt)
            for bet in match_bets.filter(status='D'):
                if total_win > 0:
                    losing_bet(bet, bet.bet_amt)
                else:  # No settlements
                    Bet.objects.filter(id=bet.id).update(status='N')

        else:  # No Settlements
            for bet in match_bets:
                Bet.objects.filter(id=bet.id).update(status='N')

    else:
        set_completed(match, win_team)
        total_lost, total_win, total_default = get_totals(bet_teams, win_team)
        if total_lost > 0:    # Default and/or lost bets were present
            for bet in match_bets.filter(bet_team=win_team):
                if total_win > 0:
                    amt = bet.bet_amt / total_win * total_lost
                    winning_bet(bet, amt)
            for bet in match_bets.exclude(bet_team=win_team):
                if total_win > 0:
                    losing_bet(bet, bet.bet_amt)
                elif total_default > 0:
                    if bet.bet_team is None:
                        losing_bet(bet, bet.bet_amt)
                    else:
                        amt = bet.bet_amt / \
                            (total_lost - total_default) * total_default
                        winning_bet(bet, amt)
                else:  # No Settlements
                    Bet.objects.filter(id=bet.id).update(status='N')
        else:  # No Settlements
            for bet in match_bets:
                Bet.objects.filter(id=bet.id).update(status='N')


def settle_ipl_winner(match, win_team):
    match_bets = Bet.objects.filter(match__isnull=True)

    bet_teams = get_team_totals(match_bets)

    total_lost, total_win, _ = get_totals(bet_teams, win_team)
    if total_lost > 0:
        for bet in match_bets.filter(bet_team=win_team):
            if total_win > 0:
                amt = bet.bet_amt / total_win * total_lost
                winning_bet(bet, amt)
        for bet in match_bets.exclude(bet_team=win_team):
            if total_win > 0:
                losing_bet(bet, bet.bet_amt)
