# Generated by Django 3.1.1 on 2020-09-03 10:08

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('ipl_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='static',
            name='bet_choices',
            field=models.CharField(default='20,40,60,80,100', max_length=20, validators=[django.core.validators.int_list_validator]),
        ),
        migrations.CreateModel(
            name='Bet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bet_amt', models.PositiveSmallIntegerField(choices=[(20, '20')], default=20)),
                ('win_amt', models.FloatField(default=0)),
                ('lost_amt', models.FloatField(default=0)),
                ('status', models.CharField(choices=[('P', 'Placed'), ('D', 'Default'), ('W', 'Won'), ('L', 'Lost'), ('N', 'No Result')], default='D', max_length=1)),
                ('create_time', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('bet_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ipl_app.team')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ipl_app.match')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.player')),
            ],
            options={
                'ordering': ['match', 'create_time'],
            },
        ),
    ]
