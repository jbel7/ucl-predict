# Generated manually
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_teamstatistic'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamstatistic',
            name='coach',
            field=models.CharField(blank=True, help_text='Current head coach', max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='ChampionsLeagueMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_date', models.DateTimeField(help_text='When the match was played')),
                ('tournament_stage', models.CharField(choices=[('GROUP', 'Group Stage'), ('R16', 'Round of 16'), ('QF', 'Quarter Finals'), ('SF', 'Semi Finals'), ('FINAL', 'Final')], max_length=10)),
                ('season', models.CharField(help_text="e.g., '2024-25'", max_length=20)),
                ('team_a_score', models.IntegerField(default=0)),
                ('team_b_score', models.IntegerField(default=0)),
                ('team_a_scorers', models.TextField(blank=True, help_text='Comma-separated list of scorers for team A')),
                ('team_b_scorers', models.TextField(blank=True, help_text='Comma-separated list of scorers for team B')),
                ('team_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ucl_matches_as_home', to='project.team')),
                ('team_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ucl_matches_as_away', to='project.team')),
            ],
            options={
                'verbose_name': 'Champions League Match',
                'verbose_name_plural': 'Champions League Matches',
                'ordering': ['-match_date'],
            },
        ),
        migrations.CreateModel(
            name='CLRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.CharField(help_text="e.g., '2024-25'", max_length=20)),
                ('wins', models.IntegerField(default=0)),
                ('draws', models.IntegerField(default=0)),
                ('losses', models.IntegerField(default=0)),
                ('goals_for', models.IntegerField(default=0)),
                ('goals_against', models.IntegerField(default=0)),
                ('stage_reached', models.CharField(help_text="e.g., 'Quarter Finals', 'Group Stage'", max_length=20)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cl_records', to='project.team')),
            ],
            options={
                'ordering': ['-season'],
                'unique_together': {('team', 'season')},
            },
        ),
    ]

