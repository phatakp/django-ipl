from django import forms
from django.forms import widgets
from django.forms.widgets import DateInput
from .models import Match, Bet


class BetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BetForm, self).__init__(*args, **kwargs)
        self.fields['bet_amt'].required = False

    class Meta:
        model = Bet
        fields = ('bet_amt', )
        labels = {'bet_amt': "Amount", }
        widgets = {'bet_amt': forms.TextInput(
            attrs={'placeholder': 'Bet Amount'})}


class MatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        self.fields['winner'].required = False

    class Meta:
        model = Match
        fields = ('winner', )


class MatchListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MatchListForm, self).__init__(*args, **kwargs)
        self.fields['home_team'].required = False
        self.fields['away_team'].required = False
        self.fields['date'].required = False

    class Meta:
        model = Match
        fields = ('home_team', 'away_team', 'date')
        widgets = {'date': DateInput(attrs={'type': 'date'})}
        labels = {'home_team': 'Team1',
                  'away_team': 'Team2', }


class BetChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BetChangeForm, self).__init__(*args, **kwargs)
        self.fields['bet_team'].required = False

    class Meta:
        model = Bet
        fields = ('bet_team',)
        labels = {'bet_team': 'New IPL Winner'}
