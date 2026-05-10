"""
URL Configuration for rooms app.
"""
from django.urls import path
from apps.rooms import views as room_views

app_name = 'rooms'

# Guest URLs
urlpatterns = [
    # Room browsing for guests
    path('rooms/', room_views.room_list, name='list'),
    path('rooms/<int:pk>/', room_views.room_detail, name='detail'),
    
    # Staff room management
    path('staff/rooms/', room_views.staff_room_list, name='staff_list'),
    path('staff/rooms/add/', room_views.staff_room_add, name='staff_add'),
    path('staff/rooms/<int:pk>/edit/', room_views.staff_room_edit, name='staff_edit'),
    path('staff/rooms/<int:pk>/delete/', room_views.staff_room_delete, name='staff_delete'),
    path('staff/rooms/<int:pk>/toggle-status/', room_views.staff_room_toggle_status, name='staff_toggle_status'),
]