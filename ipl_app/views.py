from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.apps import apps
from django.template import context
from django.views.generic import TemplateView, FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Team, Match, Bet, Static
from .forms import MatchForm, BetForm, MatchListForm, BetChangeForm
from .validations import validate_and_save, settle_bets, valid_bets, settle_ipl_winner, winning_bet
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db.models import Q, F
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

Player = apps.get_model('accounts', 'Player')
MatchHistory = apps.get_model('staff', 'MatchHistory')
AllStats = apps.get_model('staff', 'AllStats')
HomeStats = apps.get_model('staff', 'HomeStats')
AwayStats = apps.get_model('staff', 'AwayStats')
NeutralStats = apps.get_model('staff', 'NeutralStats')


class HomeView(TemplateView):
    template_name = "ipl_app/dashboard.html"

    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            return redirect('iplapp:dashboard')
        else:
            return render(request, self.template_name, context={'user': 'home'})


class DashboardView(LoginRequiredMixin, FormView):
    login_url = '/accounts/login/'
    redirect_field_name = 'ipl_app/dashboard.html'
    template_name = "ipl_app/dashboard.html"
    context = dict()

    def get_context_data(self, **kwargs):
        kwargs['form'] = None
        self.context = super().get_context_data(**kwargs)

        players = self.context.get('players', None)
        if players is None:
            self.context['players'] = Player.objects.all().select_related('user',
                                                                          'team')

            self.context['curr_player'] = self.context['players'].get(
                user=self.request.user)

        self.context['matches'] = Match.objects.filter(status='N').select_related('home_team',
                                                                                  'away_team',
                                                                                  'winner')[:2]

        player_bets = self.context.get('player_bets', None)
        if player_bets is None:
            self.context['player_bets'] = Bet.objects.filter(player=self.context['curr_player']).select_related('player__user',
                                                                                                                'match__home_team',
                                                                                                                'match__away_team',
                                                                                                                'bet_team').order_by('player__id', '-create_time')
            paginator = Paginator(self.context['player_bets'], 10)
            page = self.request.GET.get('page')
            try:
                self.context['player_bets'] = paginator.page(page)
            except PageNotAnInteger:
                self.context['player_bets'] = paginator.page(1)
            except EmptyPage:
                self.context['player_bets'] = paginator.page(
                    paginator.num_pages)

        # Get Forms
        self.context['bet_form'] = self._get_form(formcls=BetForm,
                                                  prefix="bet_")

        self.context['match_form'] = self._get_form(formcls=MatchForm,
                                                    prefix="win_")

        self.context['winner_chg_form'] = BetChangeForm()
        self.context['team_chg_msg'] = 'You will forfeit Rs.125 if you change the team'

        return self.context

    def _get_form(self, formcls, prefix):
        save_prefix = prefix
        form_list = list()
        matches = self.context.get('matches', None)
        if matches is not None:
            for i, _ in enumerate(self.context['matches']):
                prefix = f"{save_prefix}{str(i)}"
                form_list.append(formcls(prefix=prefix))
        return form_list

    def _post_form(self, formcls, prefix):
        save_prefix = prefix
        for i, _ in enumerate(self.context['matches']):
            prefix = f"{save_prefix}{str(i)}"
            data = self.request.POST if prefix in self.request.POST else None
            if data is not None:
                return formcls(data, prefix=prefix)

    def bet_form_valid(self, bet_form):
        # Get values to save to Bet model
        player = self.context['curr_player']
        match_id = self.request.POST.get('match')
        team_name = self.request.POST.get('team')
        match = Match.objects.select_related('home_team',
                                             'away_team',
                                             'winner').get(id=match_id)
        bet_team = Team.objects.get(name=team_name)
        bet_amt = self.request.POST.get(f"{bet_form.prefix}-bet_amt")

        message, success = validate_and_save(player, match, bet_team, bet_amt)

        # On successful updation of Bet model, refresh page values
        if success:
            self.context['player_bets'] = Bet.objects.filter(player=self.context['curr_player']).select_related('player__user',
                                                                                                                'match__home_team',
                                                                                                                'match__away_team',
                                                                                                                'bet_team').order_by('player__id', '-create_time')
            paginator = Paginator(self.context['player_bets'], 10)
            page = self.request.GET.get('page')
            try:
                self.context['player_bets'] = paginator.page(page)
            except PageNotAnInteger:
                self.context['player_bets'] = paginator.page(1)
            except EmptyPage:
                self.context['player_bets'] = paginator.page(
                    paginator.num_pages)

            messages.success(self.request, message)
        else:
            messages.warning(self.request, message)

        self.context['match_message'] = match

    def winner_chg_form_valid(self, new_team):
        if timezone.localtime().date() == parse_date('2020-10-13') and \
                timezone.localtime().hour < 19:
            chg_team = Team.objects.get(id=new_team)
            if chg_team != self.context['curr_player'].team:
                Bet.objects.filter(player=self.context['curr_player'],
                                   match__isnull=True).update(bet_team=chg_team,
                                                              create_time=timezone.localtime())
                Player.objects.filter(user=self.request.user).update(team=chg_team,
                                                                     team_chgd=True,
                                                                     curr_amt=F('curr_amt')-125)
                Static.objects.update(team_chg_amt=F('team_chg_amt')+125)
                self.context['team_chg_msg'] = f"IPL Winner updated to {chg_team.get_name_display()}"
                self.context['players'] = Player.objects.all().select_related('user',
                                                                              'team')
                self.context['curr_player'] = self.context['players'].get(
                    user=self.request.user)
                self.context['player_bets'] = Bet.objects.filter(player=self.context['curr_player']).select_related('player__user',
                                                                                                                    'match__home_team',
                                                                                                                    'match__away_team',
                                                                                                                    'bet_team').order_by('player__id', '-create_time')
                paginator = Paginator(self.context['player_bets'], 10)
                page = self.request.GET.get('page')
                try:
                    self.context['player_bets'] = paginator.page(page)
                except PageNotAnInteger:
                    self.context['player_bets'] = paginator.page(1)
                except EmptyPage:
                    self.context['player_bets'] = paginator.page(
                        paginator.num_pages)
            else:
                self.context['team_chg_msg'] = f"You current team is already {chg_team.get_name_display()}"
        else:
            self.context['team_chg_msg'] = f"Team Change can only be done on Oct 13th b/w 12AM & 7PM"

    def match_form_valid(self, match_form):
        match_id = self.request.POST.get('match')
        match = Match.objects.get(id=match_id)

        if valid_bets(self.context['players'].count(), match):
            if match.status == 'N':
                winner = self.request.POST.get(f"{match_form.prefix}-winner")
                win_team = Team.objects.get(
                    id=winner) if winner != '' else None
                if win_team is None or win_team in (match.home_team, match.away_team):
                    settle_bets(match, win_team)
                    if match.typ == 'F':
                        settle_ipl_winner(match, win_team)

                    self.context['players'] = Player.objects.all().select_related('user',
                                                                                  'team')
                    self.context['player_bets'] = Bet.objects.filter(player=self.context['curr_player']).select_related('player__user',
                                                                                                                        'match__home_team',
                                                                                                                        'match__away_team',
                                                                                                                        'bet_team').order_by('player__id', '-create_time')[:5]

                    messages.success(
                        self.request, f'Match Winner: {win_team.name}')

                else:
                    messages.warning(self.request, 'Winner Team not correct')
            else:
                messages.warning(self.request, 'Match Status Updated already')
        else:
            messages.warning(self.request, 'All Default Bets Not Placed')

        self.context['match_message'] = match

    def post(self, request, *args, **kwargs):
        self.context = self.get_context_data(**kwargs)

        winner_chg_form = BetChangeForm(request.POST)

        if self.context['curr_player'].staff:
            match_form = self._post_form(formcls=MatchForm,
                                         prefix="win_")
            if match_form is not None and match_form.is_valid():
                self.match_form_valid(match_form)
            else:
                bet_form = self._post_form(formcls=BetForm,
                                           prefix="bet_")
                if bet_form is not None and bet_form.is_valid():
                    self.bet_form_valid(bet_form)
                elif winner_chg_form.is_valid():
                    new_team = self.request.POST.get('bet_team')
                    self.winner_chg_form_valid(new_team)
                else:
                    match_id = self.request.POST.get('match')
                    match = Match.objects.get(id=match_id)
                    messages.warning(request, bet_form.errors['bet_amt'])
                    self.context['match_message'] = match

        else:
            bet_form = self._post_form(formcls=BetForm,
                                       prefix="bet_")

            if bet_form is not None and bet_form.is_valid():
                self.bet_form_valid(bet_form)
            elif winner_chg_form.is_valid():
                new_team = self.request.POST.get('bet_team')
                self.winner_chg_form_valid(new_team)
            else:
                match_id = self.request.POST.get('match')
                match = Match.objects.get(id=match_id)
                messages.warning(request, bet_form.errors['bet_amt'])
                self.context['match_message'] = match

        return render(request, self.template_name, self.context)


class ScheduleView(LoginRequiredMixin, ListView):
    model = Match
    login_url = '/accounts/login/'
    redirect_field_name = 'ipl_app/schedule.html'
    template_name = "ipl_app/schedule.html"
    context_object_name = 'matches'
    # paginate_by = 10

    def get_queryset(self):
        return Match.objects.select_related('home_team', 'away_team', 'winner')

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context['form'] = MatchListForm(self.request.POST or None)
        context['curr_player'] = Player.objects.select_related('user',
                                                               'team').get(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        ht = request.POST.get('home_team')
        at = request.POST.get('away_team')
        dt = request.POST.get('date')
        if dt != '':
            context['matches'] = self.object_list.filter(date=parse_date(dt))

        if ht != '':
            context['matches'] = context['matches'].filter(Q(home_team__id=ht) |
                                                           Q(away_team__id=ht))

        if at != '':
            context['matches'] = context['matches'].filter(Q(home_team__id=at) |
                                                           Q(away_team__id=at))

        return render(request, self.template_name, context)
