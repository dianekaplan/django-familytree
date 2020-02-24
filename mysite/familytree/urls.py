from django.urls import path

from . import views

urlpatterns = [
    # ex: /familytree
    path('', views.index, name='dashboard'),

    # ex: /families/
    path('families/', views.family_index, name='family_index'),

    # ex: /people/
    path('people/', views.person_index, name='person_index'),

    # ex: /people/5/
     path('people/<int:person_id>/', views.person_detail, name='person_detail'),

    # ex: /families/5/
    path('families/<int:family_id>/', views.family_detail, name='family_detail'),
]

