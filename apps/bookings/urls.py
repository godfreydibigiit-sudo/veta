"""
URL Configuration for bookings app.
"""
from django.urls import path
from apps.bookings import views

app_name = 'bookings'

urlpatterns = [
    # Guest URLs
    path('create/<int:room_id>/', views.create_booking, name='create'),
    path('confirmation/<str:reference_id>/', views.booking_confirmation, name='confirmation'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<str:reference_id>/', views.cancel_booking, name='cancel'),
    path('detail/<str:reference_id>/', views.booking_detail, name='detail'),
    
    # Staff URLs - Fixed order: specific paths first, then parameterized paths
    path('staff/list/', views.staff_booking_list, name='staff_list'),
    path('staff/search/', views.staff_search_guest, name='staff_search'),
    path('staff/today-checkins/', views.staff_today_checkins, name='staff_today_checkins'),
    path('staff/today-checkouts/', views.staff_today_checkouts, name='staff_today_checkouts'),
    path('staff/<str:reference_id>/process/', views.staff_process_booking, name='staff_process'),
    path('staff/<str:reference_id>/', views.staff_booking_detail, name='staff_detail'),
]