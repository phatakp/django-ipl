from django.apps import apps
import math

MatchHistory = apps.get_model('staff', 'MatchHistory')
AllStats = apps.get_model('staff', 'AllStats')
HomeStats = apps.get_model('staff', 'HomeStats')
AwayStats = apps.get_model('staff', 'AwayStats')
NeutralStats = apps.get_model('staff', 'NeutralStats')

venues = {'CSK': 'Chennai', 'DC': 'Delhi', 'KXIP': 'Punjab', 'KKR': 'Kolkata',
          'RR': 'Rajasthan', 'RCB': 'Bangalore', 'MI': 'Mumbai', 'SRH': 'Hyderabad'}


def get_model_values(model):
    return model.objects.select_related(
        'team1', 'team2').values_list('team1', 'team2', 'win_pct')


def last5_win_pct(home_team, away_team):
    last5 = MatchHistory.objects.select_related(
        'team1', 'team2', 'winner').all().order_by('-date')
    hm_last5 = last5.filter(team1=home_team)[:5]
    aw_last5 = last5.filter(team1=away_team)[:5]
    hm_win = hm_nr = 0
    for match in hm_last5:
        if match.winner is None:
            hm_nr += 1
        elif match.winner == home_team:
            hm_win += 1

    aw_win = aw_nr = 0
    for match in aw_last5:
        if match.winner is None:
            aw_nr += 1
        elif match.winner == away_team:
            aw_win += 1

    return (math.floor(hm_win/(5-hm_nr)*100) if hm_nr < 5 else 0,
            math.floor(aw_win/(5-aw_nr)*100) if aw_nr < 5 else 0)


def calc_percent(venue, home_team, hm, hmvs, aw, awvs, hm5, aw5):
    hm_val = list(map(lambda x: x*5, hm))
    hmvs_val = list(map(lambda x: x*11, hmvs))
    aw_val = list(map(lambda x: x*5, aw))
    awvs_val = list(map(lambda x: x*11, awvs))
    if venue == 'Neutral':
        hm_val[-1] *= 8/5
        aw_val[-1] *= 8/5
        hmvs_val[-1] *= 16/11
        awvs_val[-1] *= 16/11
    elif venue == venues[home_team.name]:
        hm_val[1] *= 8/5
        aw_val[1] *= 8/5
        hmvs_val[1] *= 16/11
        awvs_val[1] *= 16/11
    else:
        hm_val[2] *= 8/5
        aw_val[2] *= 8/5
        hmvs_val[2] *= 16/11
        awvs_val[2] *= 16/11

    ratio = (sum(hm_val) + sum(hmvs_val) + hm5*28) / \
        (sum(aw_val) + sum(awvs_val) + aw5*28)
    aw_win_pct = math.floor(100/(1+ratio))
    hm_win_pct = 100-aw_win_pct
    return (hm_win_pct, aw_win_pct)


def get_win_pct(venue, home_team, away_team):
    stats = list()
    for model in (AllStats, HomeStats, AwayStats, NeutralStats):
        stats.append(get_model_values(model))

    hm_last5_win_pct, aw_last5_win_pct = last5_win_pct(
        home_team, away_team)
    hm_win_pct = list()
    hm_vs_win_pct = list()
    aw_win_pct = list()
    aw_vs_win_pct = list()
    for _stats in stats:
        hm_win_pct.append(_stats.filter(team1=home_team,
                                        team2=None).values_list('win_pct', flat=True)[0])
        hm_vs_win_pct.append(_stats.filter(team1=home_team,
                                           team2=away_team).values_list('win_pct', flat=True)[0])
        aw_win_pct.append(_stats.filter(team1=away_team,
                                        team2=None).values_list('win_pct', flat=True)[0])
        aw_vs_win_pct.append(_stats.filter(team1=away_team,
                                           team2=home_team).values_list('win_pct', flat=True)[0])
    return calc_percent(venue,
                        home_team,
                        hm_win_pct,
                        hm_vs_win_pct,
                        aw_win_pct,
                        aw_vs_win_pct,
                        hm_last5_win_pct,
                        aw_last5_win_pct)
