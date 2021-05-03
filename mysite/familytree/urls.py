from django.conf.urls import url
from django.urls import path, include

from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ex: /familytree
    path('', views.index, name='dashboard'),

    # ex: /landing
    path('landing/', views.landing, name='landing'),

    # ex: /people/
    path('people/', views.person_index, name='person_index'),

    # ex: /people/5/
     path('people/<int:person_id>/', views.person_detail, name='person_detail'),

    # ex: /families/
    path('families/', views.family_index, name='family_index'),

    # ex: /families/5/
    path('families/<int:family_id>/', views.family_detail, name='family_detail'),

    # ex: /images/
    path('images/', views.image_index, name='image_index'),

    # ex: /images/5/
    path('images/<int:image_id>/', views.image_detail, name='image_detail'),

    # ex: /videos/
    path('videos/', views.video_index, name='video_index'),

    # ex: /videos/18/
    path('videos/<int:video_id>/', views.video_detail, name='video_detail'),

    # ex: /outline/
    path('outline/', views.outline, name='outline'),

    # ex: /history/
    path('history/', views.history, name='history'),

    # ex: /stories/4/
    path('stories/<int:story_id>/', views.story, name='story'),

    # ex: /account/
    path('account/', views.account, name='account'),

    url('^', include('django.contrib.auth.urls')), # paths for registration pages (password reset)

]
