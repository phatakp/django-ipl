from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('uphistory/', views.upload_history, name='uphistory'),
    path('matches/', views.upload_match, name='upmatch'),
    path('defaults/', views.default_bets, name='defaults'),
    path('defaults/<int:id>', views.default_bets, name='defaults'),
    path('teamstats/', views.generate_team_stats, name='teamstats'),

]
