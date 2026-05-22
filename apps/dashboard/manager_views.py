"""
Manager-specific dashboard views with full hotel oversight.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta
from apps.core.decorators import manager_required
from apps.bookings.models import Booking
from apps.rooms.models import Room
from apps.users.models import User, StaffProfile
from apps.core.models import AuditLog
from apps.core.utils import format_currency_tzs


@login_required
@manager_required
def manager_dashboard(request):
    """Main manager dashboard with comprehensive hotel overview."""
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # ===== ROOM STATS =====
    total_rooms = Room.objects.filter(is_active=True).count()
    available_rooms = Room.objects.filter(is_active=True, status='available').count()
    occupied_rooms = Room.objects.filter(is_active=True, status='occupied').count()
    occupancy_rate = round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0
    
    # ===== BOOKING STATS =====
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    checked_in_today = Booking.objects.filter(status='checked_in', check_in=today).count()
    checked_out_today = Booking.objects.filter(status='checked_out', checked_out_at__date=today).count()
    
    # ===== REVENUE STATS =====
    total_revenue = Booking.objects.filter(payment_status='paid').aggregate(
        total=Sum('total_amount'))['total'] or 0
    monthly_revenue = Booking.objects.filter(
        payment_status='paid', paid_at__gte=this_month).aggregate(
        total=Sum('total_amount'))['total'] or 0
    last_month_revenue = Booking.objects.filter(
        payment_status='paid', paid_at__gte=last_month, paid_at__lt=this_month).aggregate(
        total=Sum('total_amount'))['total'] or 0
    today_revenue = Booking.objects.filter(
        payment_status='paid', paid_at__date=today).aggregate(
        total=Sum('total_amount'))['total'] or 0
    
    revenue_change = round(((monthly_revenue - last_month_revenue) / last_month_revenue * 100), 1) if last_month_revenue > 0 else 0
    
    # ===== STAFF STATS =====
    total_staff = User.objects.filter(role__in=['staff', 'manager']).count()
    active_staff = User.objects.filter(role__in=['staff', 'manager'], is_active=True).count()
    
    # ===== RECENT ACTIVITIES =====
    recent_audit_logs = AuditLog.objects.select_related('user').order_by('-created_at')[:20]
    recent_bookings = Booking.objects.select_related('guest', 'room').order_by('-created_at')[:10]
    recent_checkins = Booking.objects.filter(status='checked_in').select_related('guest', 'room').order_by('-checked_in_at')[:5]
    
    # ===== TODAY'S SUMMARY =====
    today_checkins = Booking.objects.filter(check_in=today, status__in=['approved', 'pending']).select_related('guest', 'room')
    today_checkouts = Booking.objects.filter(check_out=today, status='checked_in').select_related('guest', 'room')
    
    # ===== REVENUE CHART DATA =====
    daily_revenue = []
    for i in range(7):
        date = today - timedelta(days=i)
        revenue = Booking.objects.filter(payment_status='paid', paid_at__date=date).aggregate(
            total=Sum('total_amount'))['total'] or 0
        daily_revenue.append({
            'date': date.strftime('%a'),
            'revenue': int(revenue),
            'date_full': date.strftime('%d %b'),
        })
    daily_revenue.reverse()
    
    # ===== ROOM TYPE DISTRIBUTION =====
    room_types = Room.objects.filter(is_active=True).values('room_type').annotate(
        count=Count('id')).order_by('room_type')
    
    stats = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'occupancy_rate': occupancy_rate,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'checked_in_today': checked_in_today,
        'checked_out_today': checked_out_today,
        'total_revenue': format_currency_tzs(total_revenue),
        'monthly_revenue': format_currency_tzs(monthly_revenue),
        'last_month_revenue': format_currency_tzs(last_month_revenue),
        'today_revenue': format_currency_tzs(today_revenue),
        'revenue_change': revenue_change,
        'total_staff': total_staff,
        'active_staff': active_staff,
        'recent_audit_logs': recent_audit_logs,
        'recent_bookings': recent_bookings,
        'recent_checkins': recent_checkins,
        'today_checkins': today_checkins,
        'today_checkouts': today_checkouts,
        'daily_revenue': daily_revenue,
        'room_types': room_types,
    }
    
    return render(request, 'dashboard/manager/index.html', {'stats': stats})