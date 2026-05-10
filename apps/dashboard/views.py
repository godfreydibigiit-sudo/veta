"""
Dashboard views for staff management and statistics.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta
from apps.core.decorators import staff_required
from apps.bookings.models import Booking
from apps.bookings.services import BookingService
from apps.rooms.models import Room
from apps.users.models import User
from apps.core.utils import format_currency_tzs


@login_required
@staff_required
def dashboard(request):
    """
    Main staff dashboard with live statistics.
    """
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # ========== ROOM STATISTICS ==========
    total_rooms = Room.objects.filter(is_active=True).count()
    available_rooms = Room.objects.filter(
        is_active=True, status='available'
    ).count()
    occupied_rooms = Room.objects.filter(
        is_active=True, status='occupied'
    ).count()
    maintenance_rooms = Room.objects.filter(
        is_active=True, status='maintenance'
    ).count()
    reserved_rooms = Room.objects.filter(
        is_active=True, status='reserved'
    ).count()
    
    # ========== BOOKING STATISTICS ==========
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    approved_bookings = Booking.objects.filter(status='approved').count()
    checked_in_today = Booking.objects.filter(
        status='checked_in',
        check_in=today
    ).count()
    checked_out_today = Booking.objects.filter(
        status='checked_out',
        checked_out_at__date=today
    ).count()
    
    # Currently checked in
    currently_checked_in = Booking.objects.filter(
        status='checked_in'
    ).select_related('guest', 'room').order_by('check_in')
    
    # ========== REVENUE STATISTICS ==========
    total_revenue = Booking.objects.filter(
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    monthly_revenue = Booking.objects.filter(
        payment_status='paid',
        paid_at__gte=this_month
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    last_month_revenue = Booking.objects.filter(
        payment_status='paid',
        paid_at__gte=last_month,
        paid_at__lt=this_month
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Today's revenue
    today_revenue = Booking.objects.filter(
        payment_status='paid',
        paid_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # ========== GUEST STATISTICS ==========
    total_guests = User.objects.filter(role='guest').count()
    new_guests_today = User.objects.filter(
        role='guest',
        date_joined__date=today
    ).count()
    
    # ========== RECENT ACTIVITY ==========
    recent_bookings = Booking.objects.select_related(
        'guest', 'room', 'processed_by'
    ).order_by('-updated_at')[:10]
    
    recent_checkins = Booking.objects.filter(
        status='checked_in'
    ).select_related('guest', 'room').order_by('-checked_in_at')[:5]
    
    # ========== UPCOMING ==========
    upcoming_checkins = Booking.objects.filter(
        check_in=today + timedelta(days=1),
        status__in=['approved', 'pending']
    ).select_related('guest', 'room').order_by('created_at')
    
    upcoming_checkouts = Booking.objects.filter(
        check_out=today + timedelta(days=1),
        status='checked_in'
    ).select_related('guest', 'room').order_by('room__room_number')
    
    # ========== ROOM TYPE DISTRIBUTION ==========
    room_type_distribution = Room.objects.filter(
        is_active=True
    ).values('room_type').annotate(
        count=Count('id')
    ).order_by('room_type')
    
    # ========== OCCUPANCY RATE ==========
    occupancy_rate = 0
    if total_rooms > 0:
        occupancy_rate = round((occupied_rooms / total_rooms) * 100, 1)
    
    stats = {
        # Room stats
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'reserved_rooms': reserved_rooms,
        'occupancy_rate': occupancy_rate,
        'room_type_distribution': room_type_distribution,
        
        # Booking stats
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'checked_in_today': checked_in_today,
        'checked_out_today': checked_out_today,
        'currently_checked_in': currently_checked_in,
        'currently_checked_in_count': currently_checked_in.count(),
        
        # Revenue stats
        'total_revenue': format_currency_tzs(total_revenue),
        'total_revenue_raw': total_revenue,
        'monthly_revenue': format_currency_tzs(monthly_revenue),
        'monthly_revenue_raw': monthly_revenue,
        'last_month_revenue': format_currency_tzs(last_month_revenue),
        'today_revenue': format_currency_tzs(today_revenue),
        'revenue_change_percent': calculate_percentage_change(
            monthly_revenue, last_month_revenue
        ),
        
        # Guest stats
        'total_guests': total_guests,
        'new_guests_today': new_guests_today,
        
        # Recent activity
        'recent_bookings': recent_bookings,
        'recent_checkins': recent_checkins,
        
        # Upcoming
        'upcoming_checkins': upcoming_checkins,
        'upcoming_checkins_count': upcoming_checkins.count(),
        'upcoming_checkouts': upcoming_checkouts,
        'upcoming_checkouts_count': upcoming_checkouts.count(),
    }
    
    return render(request, 'staff/dashboard/index.html', {'stats': stats})


@login_required
@staff_required
def reports_view(request):
    """
    Staff view: Reports and analytics.
    """
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Daily revenue for last 30 days
    daily_revenue = []
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        revenue = Booking.objects.filter(
            payment_status='paid',
            paid_at__date=date
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        bookings_count = Booking.objects.filter(
            created_at__date=date
        ).count()
        
        daily_revenue.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(revenue),
            'bookings': bookings_count,
        })
    
    # Booking status distribution
    status_distribution = Booking.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Monthly statistics
    monthly_stats = []
    for i in range(12):
        month_date = today.replace(day=1) - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year+1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month+1, day=1) - timedelta(days=1)
        
        revenue = Booking.objects.filter(
            payment_status='paid',
            paid_at__date__gte=month_start,
            paid_at__date__lte=month_end
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        bookings = Booking.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%B %Y'),
            'revenue': float(revenue),
            'bookings': bookings,
        })
    
    context = {
        'daily_revenue': daily_revenue,
        'status_distribution': status_distribution,
        'monthly_stats': monthly_stats,
    }
    
    return render(request, 'staff/dashboard/reports.html', context)


@login_required
@staff_required
def quick_search(request):
    """
    Quick search for guest by phone or reference ID.
    Returns booking and guest information.
    """
    query = request.GET.get('q', '').strip()
    results = None
    guest = None
    error = None
    
    if query:
        from apps.core.utils import search_bookings_by_guest
        bookings = search_bookings_by_guest(query)
        
        if not bookings.exists():
            # Try finding guest directly
            guest = User.objects.filter(
                Q(phone__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).filter(role='guest').first()
            
            if guest:
                bookings = guest.bookings.select_related(
                    'room'
                ).order_by('-created_at')
        
        results = bookings[:10] if bookings else None
        
        if not results and not guest:
            error = 'No guest or booking found.'
    
    context = {
        'query': query,
        'results': results,
        'guest': guest,
        'error': error,
    }
    
    return render(request, 'staff/dashboard/quick_search_results.html', context)


@login_required
@staff_required
def get_realtime_stats(request):
    """
    AJAX endpoint for real-time dashboard updates.
    Returns JSON data for dashboard widgets.
    """
    from django.http import JsonResponse
    
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    today = timezone.now().date()
    
    stats = {
        'available_rooms': Room.objects.filter(
            is_active=True, status='available'
        ).count(),
        'occupied_rooms': Room.objects.filter(
            is_active=True, status='occupied'
        ).count(),
        'checked_in_today': Booking.objects.filter(
            status='checked_in', check_in=today
        ).count(),
        'today_revenue': float(
            Booking.objects.filter(
                payment_status='paid', paid_at__date=today
            ).aggregate(total=Sum('total_amount'))['total'] or 0
        ),
        'pending_bookings': Booking.objects.filter(
            status='pending'
        ).count(),
    }
    
    return JsonResponse(stats)


# ============= HELPER FUNCTIONS =============

def calculate_percentage_change(current, previous):
    """
    Calculate percentage change between two values.
    """
    if previous == 0:
        return 100 if current > 0 else 0
    
    change = ((current - previous) / previous) * 100
    return round(change, 1)