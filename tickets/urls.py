# tickets/urls.py
from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.ticket_list, name='list'),  # All tickets (agents) / My tickets (end-users)
    path('submit/', views.ticket_submit, name='submit'),
    path('queue/my/', views.ticket_list, name='my_queue'),  # Reuse ticket_list
    path('api/canned-responses/', views.canned_responses_api, name='canned_responses_api'),
    path('<str:ticket_id>/escalate/', views.ticket_escalate, name='escalate'),
    path('<str:ticket_id>/', views.ticket_detail, name='detail'),
]