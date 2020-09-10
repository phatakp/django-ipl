from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'accounts'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(template_name='accounts/login.html'), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('pwdchg/', views.UserPwdChangeView.as_view(), name='pwd_change'),
]
