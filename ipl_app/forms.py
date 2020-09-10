from django import forms
from django.forms import widgets
from django.forms.widgets import HiddenInput
from .models import Match, Bet
from django.utils import timezone


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


class BetListForm(forms.ModelForm):
    class Meta:
        model = Bet
        exclude = "__all__"
        widgets = {'player': forms.HiddenInput()}
