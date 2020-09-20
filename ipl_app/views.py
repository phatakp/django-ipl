from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.apps import apps
from django.template import context
from django.views.generic import TemplateView, FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Team, Match, Bet
from .forms import MatchForm, BetForm, BetListForm
from .validations import validate_and_save, settle_bets, valid_bets, settle_ipl_winner
from django.utils import timezone

from django.db.models import Q
from django.contrib import messages

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

        self.context['match_dates'] = Match.objects.filter(status='N').values_list(
            'date', flat=True).distinct()[:2]

        date_count = len(self.context['match_dates'])

        if date_count > 1:
            self.context['matches'] = Match.objects.filter(Q(date=self.context['match_dates'][0]) |
                                                           Q(date=self.context['match_dates'][1])).select_related('home_team',
                                                                                                                  'away_team',
                                                                                                                  'winner')
        elif date_count > 0:
            self.context['matches'] = Match.objects.filter(date=self.context['match_dates'][0]).select_related('home_team',
                                                                                                               'away_team',
                                                                                                               'winner')

        player_bets = self.context.get('player_bets', None)
        if player_bets is None:
            self.context['player_bets'] = Bet.objects.filter(player=self.context['curr_player']).select_related('player__user',
                                                                                                                'match__home_team',
                                                                                                                'match__away_team',
                                                                                                                'bet_team').order_by('player__id', '-create_time')[:5]

        # Get Forms
        self.context['bet_form'] = self._get_form(formcls=BetForm,
                                                  prefix="bet_")

        self.context['match_form'] = self._get_form(formcls=MatchForm,
                                                    prefix="win_")

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
                                                                                                                'bet_team').order_by('player__id', '-create_time')[:5]
            messages.success(self.request, message)
        else:
            messages.warning(self.request, message)

        self.context['match_message'] = match

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

                    messages.success(self.request, 'Match Winner updated')

                else:
                    messages.warning(self.request, 'Winner Team not correct')
            else:
                messages.warning(self.request, 'Match Status Updated already')
        else:
            messages.warning(self.request, 'All Default Bets Not Placed')

        self.context['match_message'] = match

    def post(self, request, *args, **kwargs):
        self.context = self.get_context_data(**kwargs)

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
    paginate_by = 10
    form = BetListForm

    def get_queryset(self):
        return Match.objects.all().order_by('status','date')

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context['match_id'] = kwargs.get('id', None)
        if context['match_id'] is not None:
            match_date = Match.objects.get(id=context['match_id']).date
            if timezone.localtime().date() > match_date or \
                    (timezone.localtime().date() == match_date and timezone.localtime().hour >= 12):
                context['bets'] = Bet.objects.filter(match__id=context['match_id']).select_related('player',
                                                                                                   'match',
                                                                                                   'bet_team')
        context['curr_player'] = Player.objects.get(user=self.request.user)
        return render(request, self.template_name, context)
