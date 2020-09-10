from django.urls import path
from . import views

app_name = 'iplapp'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('schedule/', views.ScheduleView.as_view(), name='schedule'),
    path('schedule/<int:id>', views.ScheduleView.as_view(), name='schedule'),
]
