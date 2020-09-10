from django.db import models
from django.core.validators import int_list_validator
from django.utils import timezone


class Static(models.Model):
    CHOICE = ','.join(['20', '40', '60', '80', '100'])
    bet_choices = models.CharField(max_length=20,
                                   validators=[int_list_validator, ],
                                   default=CHOICE)


class Team(models.Model):
    """Teams in IPL 2020"""

    TEAM_CHOICES = [('CSK', 'Chennai Super Kings'),
                    ('DC', 'Delhi Capitals'),
                    ('KXIP', 'Kings XI Punjab'),
                    ('KKR', 'Kolkata Knightriders'),
                    ('MI', 'Mumbai Indians'),
                    ('RR', 'Rajasthan Royals'),
                    ('RCB', 'Royal Challengers Bangalore'),
                    ('SRH', 'Sunrisers Hyderabad'),
                    ]
    # Model Fields
    name = models.CharField(max_length=4,
                            choices=TEAM_CHOICES,
                            unique=True)

    back_color = models.CharField(max_length=7)

    fore_color = models.CharField(max_length=7)

    i_height = models.PositiveSmallIntegerField(default=100)

    i_width = models.PositiveSmallIntegerField(default=100)

    logo = models.ImageField()

    def __str__(self):
        """Unicode representation of Team."""
        return self.name


class Match(models.Model):
    """Match in IPL 2020."""

    STATUS_CHOICES = [('P', 'Completed'),
                      ('N', 'Scheduled'),
                      ('A', 'Abandoned')
                      ]

    TYPE_CHOICES = [('L', 'League'),
                    ('E', 'Eliminator'),
                    ('F', 'Final'),
                    ('P1', 'Playoff1'),
                    ('P2', 'Playoff2'),
                    ]

    # Model Fields
    num = models.PositiveSmallIntegerField(unique=True)

    date = models.DateField()

    home_team = models.ForeignKey(Team,
                                  related_name='home_teams',
                                  on_delete=models.CASCADE,
                                  blank=True, null=True)

    away_team = models.ForeignKey(Team,
                                  related_name='away_teams',
                                  on_delete=models.CASCADE,
                                  blank=True, null=True)

    venue = models.CharField(max_length=30)

    status = models.CharField(max_length=1,
                              choices=STATUS_CHOICES,
                              default='N',
                              db_index=True)

    typ = models.CharField(max_length=2,
                           choices=TYPE_CHOICES,
                           default='L',
                           db_index=True)

    winner = models.ForeignKey(Team,
                               related_name='win',
                               on_delete=models.CASCADE,
                               blank=True, null=True)

    home_win_pct = models.PositiveSmallIntegerField(default=0)

    away_win_pct = models.PositiveSmallIntegerField(default=0)

    min_bet = models.PositiveSmallIntegerField(default=20)

    class Meta:
        """Meta definition for Match."""
        ordering = ['date', ]

    def __str__(self):
        """Unicode representation of Match."""
        if self.home_team is not None:
            return f"{str(self.home_team)} vs {str(self.away_team)}"
        else:
            return self.get_typ_display()


class Bet(models.Model):
    STATUS_CHOICES = [('P', 'Placed'),
                      ('D', 'Default'),
                      ('W', 'Won'),
                      ('L', 'Lost'),
                      ('N', 'No Result')]

    # Model Fields
    player = models.ForeignKey('accounts.Player',
                               related_name="bets",
                               on_delete=models.CASCADE)

    match = models.ForeignKey('ipl_app.Match',
                              related_name="matches",
                              on_delete=models.CASCADE,
                              blank=True, null=True)

    bet_team = models.ForeignKey('ipl_app.Team',
                                 related_name="teams",
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True)

    bet_amt = models.PositiveSmallIntegerField()

    win_amt = models.FloatField(default=0)

    lost_amt = models.FloatField(default=0)

    status = models.CharField(max_length=1,
                              default='D',
                              choices=STATUS_CHOICES,
                              db_index=True)

    create_time = models.DateTimeField(default=timezone.localtime,
                                       db_index=True)

    class Meta:
        ordering = ['match', 'create_time']

    def __str__(self) -> str:
        if self.match is not None:
            return f"{self.player.user.username} for {str(self.match)}"
        else:
            return f"{self.player.user.username} for IPL Winner"
