from django.db import models


class MatchHistory(models.Model):
    """Historical Match Results in IPL"""

    # Model Fields
    date = models.DateField()

    team1 = models.ForeignKey(
        'ipl_app.Team', related_name='home_hist', on_delete=models.CASCADE)

    team2 = models.ForeignKey(
        'ipl_app.Team', related_name='away_hist', on_delete=models.CASCADE)
    venue = models.CharField(max_length=30)

    winner = models.ForeignKey(
        'ipl_app.Team', related_name='win_hist', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        """Meta definition for Match."""
        ordering = ['team1', 'team2', 'date']

    def __str__(self):
        """Unicode representation of Match History"""
        return f"{str(self.team1)} vs {str(self.team2)} on {str(self.date)}"


class AllStats(models.Model):

    team1 = models.ForeignKey(
        'ipl_app.Team', related_name="team1", on_delete=models.CASCADE)

    team2 = models.ForeignKey(
        'ipl_app.Team', related_name="team2", on_delete=models.CASCADE, blank=True, null=True)

    matches = models.PositiveSmallIntegerField(default=0)

    wins = models.PositiveSmallIntegerField(default=0)

    loss = models.PositiveSmallIntegerField(default=0)

    no_result = models.PositiveSmallIntegerField(default=0)

    win_pct = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['team1', 'team2']

    def __str__(self) -> str:
        if self.team2 is not None:
            return f"{self.team1.name}vs{self.team2.name}"
        else:
            return f"{self.team1.name}"


class HomeStats(models.Model):

    team1 = models.ForeignKey(
        'ipl_app.Team', related_name="hteam1", on_delete=models.CASCADE)

    team2 = models.ForeignKey(
        'ipl_app.Team', related_name="hteam2", on_delete=models.CASCADE, blank=True, null=True)

    matches = models.PositiveSmallIntegerField(default=0)

    wins = models.PositiveSmallIntegerField(default=0)

    loss = models.PositiveSmallIntegerField(default=0)

    no_result = models.PositiveSmallIntegerField(default=0)

    win_pct = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['team1', 'team2']

    def __str__(self) -> str:
        if self.team2 is not None:
            return f"{self.team1.name}vs{self.team2.name}"
        else:
            return f"{self.team1.name}"


class AwayStats(models.Model):

    team1 = models.ForeignKey(
        'ipl_app.Team', related_name="ateam1", on_delete=models.CASCADE)

    team2 = models.ForeignKey(
        'ipl_app.Team', related_name="ateam2", on_delete=models.CASCADE, blank=True, null=True)

    matches = models.PositiveSmallIntegerField(default=0)

    wins = models.PositiveSmallIntegerField(default=0)

    loss = models.PositiveSmallIntegerField(default=0)

    no_result = models.PositiveSmallIntegerField(default=0)

    win_pct = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['team1', 'team2']

    def __str__(self) -> str:
        if self.team2 is not None:
            return f"{self.team1.name}vs{self.team2.name}"
        else:
            return f"{self.team1.name}"


class NeutralStats(models.Model):

    team1 = models.ForeignKey(
        'ipl_app.Team', related_name="nteam1", on_delete=models.CASCADE)

    team2 = models.ForeignKey(
        'ipl_app.Team', related_name="nteam2", on_delete=models.CASCADE, blank=True, null=True)

    matches = models.PositiveSmallIntegerField(default=0)

    wins = models.PositiveSmallIntegerField(default=0)

    loss = models.PositiveSmallIntegerField(default=0)

    no_result = models.PositiveSmallIntegerField(default=0)

    win_pct = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['team1', 'team2']

    def __str__(self) -> str:
        if self.team2 is not None:
            return f"{self.team1.name}vs{self.team2.name}"
        else:
            return f"{self.team1.name}"
