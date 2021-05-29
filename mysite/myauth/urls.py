from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as my_auth_views  # for clarity

urlpatterns = (
    path('login/', my_auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # ... see list at:
    # https://docs.djangoproject.com/en/3.2/topics/auth/default/#using-the-views
)