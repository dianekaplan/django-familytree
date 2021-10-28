from django.conf.urls import url
from django.urls import path, include, re_path

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

    # ex: /add_note/person/5/
    path('add_note/<str:object_type>/<int:object_id>/', views.add_note, name='add_person_note'),

    # ex: /add_note/family/5/
    path('add_note/<str:object_type>/<int:object_id>/', views.add_note, name='add_family_note'),

    # ex: /edit_person/5/
    path('edit_person/<int:person_id>/', views.edit_person, name='edit_person'),

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

    # ex: /user_metrics/
    path('user_metrics/', views.user_metrics, name='user_metrics'),

    re_path('^', include('django.contrib.auth.urls')),  # paths for registration pages (password reset)

]
