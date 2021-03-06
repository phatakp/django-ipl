# Generated by Django 3.1.1 on 2020-09-08 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ipl_app', '0009_auto_20200907_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='min_bet',
            field=models.PositiveSmallIntegerField(default=20),
        ),
        migrations.AlterField(
            model_name='bet',
            name='bet_amt',
            field=models.PositiveSmallIntegerField(default=20),
        ),
        migrations.AlterField(
            model_name='match',
            name='away_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='away_teams', to='ipl_app.team'),
        ),
        migrations.AlterField(
            model_name='match',
            name='home_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='home_teams', to='ipl_app.team'),
        ),
        migrations.AlterField(
            model_name='match',
            name='typ',
            field=models.CharField(choices=[('L', 'League'), ('E', 'Eliminator'), ('F', 'Final'), ('P1', 'Playoff1'), ('P2', 'Playoff2')], db_index=True, default='L', max_length=2),
        ),
    ]
