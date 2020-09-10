from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from django.views.generic import FormView
from .forms import UserRegistrationForm, PlayerForm, UserLoginForm, UserPwdChangeForm
from django.apps import apps

Bet = apps.get_model('ipl_app', 'Bet')


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = UserLoginForm

    def form_valid(self, form):
        return super().form_valid(form)


class UserRegistrationView(FormView):
    template_name = 'accounts/register.html'
    error = False

    def get(self, request, *args, **kwargs):
        user_form = UserRegistrationForm()
        player_form = PlayerForm()
        context = {'user_form': user_form,
                   'player_form': player_form,
                   'error': self.error}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(request.POST)
        player_form = PlayerForm(request.POST)
        error = False

        if user_form.is_valid() and player_form.is_valid():
            user = user_form.save()
            player = player_form.save(commit=False)
            player.user = user
            player.save()
            Bet.objects.create(player=player,
                               bet_team=player.team,
                               bet_amt=250,
                               status='P')
            return redirect('accounts:login')
        else:
            error = True
            context = {'user_form': user_form,
                       'player_form': player_form,
                       'error': error}
            return render(request, self.template_name, context)


class UserPwdChangeView(PasswordChangeView):
    template_name = 'accounts/pwd_change.html'
    form_class = UserPwdChangeForm
    success_url = reverse_lazy('accounts:pwd_change')

    def get_form_kwargs(self):
        kwargs = super(UserPwdChangeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        context = self.get_context_data()
        context['message'] = "Your Password has been changed successfully!"
        return render(self.request, self.template_name, context)
