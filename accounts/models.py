from django.db import models
from django.conf import settings


class Player(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)

    team = models.ForeignKey('ipl_app.Team',
                             on_delete=models.CASCADE)

    staff = models.BooleanField(default=False)

    curr_amt = models.FloatField(default=0)

    bets_won = models.PositiveSmallIntegerField(default=0)

    bets_lost = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['-curr_amt', ]

    def __str__(self) -> str:
        return self.user.username
