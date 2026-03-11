from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('', views.kb_home, name='home'),
    path('article/create/', views.article_create, name='article_create'),
    path('article/<slug:slug>/', views.article_detail, name='article'),
    path('article/<slug:slug>/edit/', views.article_edit, name='article_edit'),
]
