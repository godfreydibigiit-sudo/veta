"""
Dashboard views for staff and manager management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta
from apps.core.decorators import staff_required
from apps.bookings.models import Booking
from apps.bookings.services import BookingService
from apps.rooms.models import Room
from apps.users.models import User
from apps.core.models import AuditLog
from apps.core.utils import format_currency_tzs
from apps.users.forms import StaffRegistrationForm
from django.contrib import messages


def is_manager(user):
    """Check if user is a hotel manager."""
    return user.is_authenticated and hasattr(user, 'is_manager') and user.is_manager()


def manager_required(view_func):
    """Decorator for manager-only views."""
    from functools import wraps
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib import messages
            messages.error(request, 'Please login to access this area.')
            return redirect('users:staff_login')
        
        if not is_manager(request.user) and not request.user.is_admin():
            from django.contrib import messages
            messages.error(request, 'Only hotel managers can access this area.')
            return redirect('dashboard:index')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ============================================
# STAFF DASHBOARD
# ============================================

@login_required
@staff_required
def dashboard(request):
    """
    Main staff dashboard with live statistics.
    """
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # Room statistics
    total_rooms = Room.objects.filter(is_active=True).count()
    available_rooms = Room.objects.filter(is_active=True, status='available').count()
    occupied_rooms = Room.objects.filter(is_active=True, status='occupied').count()
    maintenance_rooms = Room.objects.filter(is_active=True, status='maintenance').count()
    
    # Booking statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    approved_bookings = Booking.objects.filter(status='approved').count()
    checked_in_today = Booking.objects.filter(status='checked_in', check_in=today).count()
    checked_out_today = Booking.objects.filter(status='checked_out', checked_out_at__date=today).count()
    
    currently_checked_in = Booking.objects.filter(status='checked_in').select_related('guest', 'room').order_by('check_in')
    
    # Revenue statistics
    total_revenue = Booking.objects.filter(payment_status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
    monthly_revenue = Booking.objects.filter(payment_status='paid', paid_at__gte=this_month).aggregate(total=Sum('total_amount'))['total'] or 0
    last_month_revenue = Booking.objects.filter(payment_status='paid', paid_at__gte=last_month, paid_at__lt=this_month).aggregate(total=Sum('total_amount'))['total'] or 0
    today_revenue = Booking.objects.filter(payment_status='paid', paid_at__date=today).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Guest statistics
    total_guests = User.objects.filter(role='guest').count()
    
    # Recent activity
    recent_bookings = Booking.objects.select_related('guest', 'room', 'processed_by').order_by('-updated_at')[:10]
    
    # Upcoming
    tomorrow = today + timedelta(days=1)
    upcoming_checkins = Booking.objects.filter(check_in=tomorrow, status__in=['approved', 'pending']).select_related('guest', 'room').order_by('created_at')
    upcoming_checkouts = Booking.objects.filter(check_out=tomorrow, status='checked_in').select_related('guest', 'room').order_by('room__room_number')
    
    # Occupancy rate
    occupancy_rate = 0
    if total_rooms > 0:
        occupancy_rate = round((occupied_rooms / total_rooms) * 100, 1)
    
    stats = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'occupancy_rate': occupancy_rate,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'checked_in_today': checked_in_today,
        'checked_out_today': checked_out_today,
        'currently_checked_in': currently_checked_in,
        'currently_checked_in_count': currently_checked_in.count(),
        'total_revenue': format_currency_tzs(total_revenue),
        'monthly_revenue': format_currency_tzs(monthly_revenue),
        'last_month_revenue': format_currency_tzs(last_month_revenue),
        'today_revenue': format_currency_tzs(today_revenue),
        'total_guests': total_guests,
        'recent_bookings': recent_bookings,
        'upcoming_checkins': upcoming_checkins,
        'upcoming_checkins_count': upcoming_checkins.count(),
        'upcoming_checkouts': upcoming_checkouts,
        'upcoming_checkouts_count': upcoming_checkouts.count(),
    }
    
    return render(request, 'staff/dashboard/index.html', {'stats': stats})


# ============================================
# MANAGER DASHBOARD
# ============================================

@login_required
def manager_dashboard(request):
    """
    Manager dashboard with comprehensive hotel oversight.
    """
    # Check if user is manager
    if not request.user.is_manager() and not request.user.is_admin():
        messages.error(request, 'Access denied. Manager privileges required.')
        return redirect('dashboard:index')
    
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # ===== ROOM STATS =====
    total_rooms = Room.objects.filter(is_active=True).count()
    available_rooms = Room.objects.filter(is_active=True, status='available').count()
    occupied_rooms = Room.objects.filter(is_active=True, status='occupied').count()
    occupancy_rate = round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0
    
    # ===== BOOKING STATS =====
    pending_bookings = Booking.objects.filter(status='pending').count()
    approved_bookings = Booking.objects.filter(status='approved').count()
    checked_in_today = Booking.objects.filter(status='checked_in', check_in=today).count()
    checked_out_today = Booking.objects.filter(status='checked_out', checked_out_at__date=today).count()
    currently_checked_in = Booking.objects.filter(status='checked_in').select_related('guest', 'room')
    
    # ===== REVENUE STATS =====
    total_revenue = Booking.objects.filter(payment_status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
    monthly_revenue = Booking.objects.filter(payment_status='paid', paid_at__gte=this_month).aggregate(total=Sum('total_amount'))['total'] or 0
    last_month_revenue = Booking.objects.filter(payment_status='paid', paid_at__gte=last_month, paid_at__lt=this_month).aggregate(total=Sum('total_amount'))['total'] or 0
    today_revenue = Booking.objects.filter(payment_status='paid', paid_at__date=today).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # ===== STAFF STATS =====
    total_staff = User.objects.filter(role__in=['staff', 'manager'], is_active=True).count()
    
    # ===== GUEST STATS =====
    total_guests = User.objects.filter(role='guest').count()
    
    # ===== RECENT ACTIVITIES =====
    recent_bookings = Booking.objects.select_related('guest', 'room').order_by('-created_at')[:10]
    recent_checkins = Booking.objects.filter(status='checked_in').select_related('guest', 'room').order_by('-checked_in_at')[:5]
    
    # ===== UPCOMING =====
    tomorrow = today + timedelta(days=1)
    upcoming_checkins = Booking.objects.filter(check_in=tomorrow, status__in=['approved', 'pending']).select_related('guest', 'room')
    upcoming_checkouts = Booking.objects.filter(check_out=tomorrow, status='checked_in').select_related('guest', 'room')
    
    stats = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'occupancy_rate': occupancy_rate,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'checked_in_today': checked_in_today,
        'checked_out_today': checked_out_today,
        'currently_checked_in': currently_checked_in,
        'currently_checked_in_count': currently_checked_in.count(),
        'total_revenue': format_currency_tzs(total_revenue),
        'monthly_revenue': format_currency_tzs(monthly_revenue),
        'last_month_revenue': format_currency_tzs(last_month_revenue),
        'today_revenue': format_currency_tzs(today_revenue),
        'total_staff': total_staff,
        'total_guests': total_guests,
        'recent_bookings': recent_bookings,
        'recent_checkins': recent_checkins,
        'upcoming_checkins': upcoming_checkins,
        'upcoming_checkins_count': upcoming_checkins.count(),
        'upcoming_checkouts': upcoming_checkouts,
        'upcoming_checkouts_count': upcoming_checkouts.count(),
    }
    
    # IMPORTANT: Render the MANAGER template, not the staff template
    return render(request, 'staff/dashboard/manager_dashboard.html', {'stats': stats})


# ============================================
# COMMON VIEWS
# ============================================

@login_required
@staff_required
def reports_view(request):
    """
    Staff/Manager view: Reports and analytics.
    """
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Daily revenue for last 30 days
    daily_revenue = []
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        revenue = Booking.objects.filter(payment_status='paid', paid_at__date=date).aggregate(total=Sum('total_amount'))['total'] or 0
        bookings_count = Booking.objects.filter(created_at__date=date).count()
        daily_revenue.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(revenue),
            'bookings': bookings_count,
        })
    
    # Booking status distribution
    status_distribution = Booking.objects.values('status').annotate(count=Count('id')).order_by('status')
    
    # Monthly statistics
    monthly_stats = []
    for i in range(12):
        month_date = today.replace(day=1) - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year+1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month+1, day=1) - timedelta(days=1)
        
        revenue = Booking.objects.filter(payment_status='paid', paid_at__date__gte=month_start, paid_at__date__lte=month_end).aggregate(total=Sum('total_amount'))['total'] or 0
        bookings = Booking.objects.filter(created_at__date__gte=month_start, created_at__date__lte=month_end).count()
        
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
    """
    query = request.GET.get('q', '').strip()
    results = None
    guest = None
    error = None
    
    if query:
        from apps.core.utils import search_bookings_by_guest
        bookings = search_bookings_by_guest(query)
        
        if not bookings.exists():
            guest = User.objects.filter(
                Q(phone__icontains=query) | Q(email__icontains=query) |
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ).filter(role='guest').first()
            
            if guest:
                bookings = guest.bookings.select_related('room').order_by('-created_at')
        
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
    """
    from django.http import JsonResponse
    
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    today = timezone.now().date()
    
    stats = {
        'available_rooms': Room.objects.filter(is_active=True, status='available').count(),
        'occupied_rooms': Room.objects.filter(is_active=True, status='occupied').count(),
        'checked_in_today': Booking.objects.filter(status='checked_in', check_in=today).count(),
        'today_revenue': float(Booking.objects.filter(payment_status='paid', paid_at__date=today).aggregate(total=Sum('total_amount'))['total'] or 0),
        'pending_bookings': Booking.objects.filter(status='pending').count(),
    }
    
    return JsonResponse(stats)


@login_required
@staff_required
def staff_list(request):
    """List all staff members."""
    staff_users = User.objects.filter(role__in=['staff', 'manager', 'admin']).order_by('-date_joined')
    
    return render(request, 'staff/users/staff_list.html', {
        'staff_users': staff_users,
        'total_staff': staff_users.count()
    })


@login_required
@staff_required
def guest_list(request):
    """List all registered guests."""
    guests = User.objects.filter(role='guest').order_by('-date_joined')
    
    return render(request, 'staff/users/guest_list.html', {
        'guests': guests,
        'total_guests': guests.count()
    })


@login_required
@staff_required
def user_detail(request, pk):
    """View user details."""
    user = get_object_or_404(User.objects.select_related('staff_profile'), pk=pk)
    bookings = user.bookings.select_related('room').order_by('-created_at')
    
    return render(request, 'staff/users/user_detail.html', {
        'user_profile': user,
        'bookings': bookings[:10],
        'total_bookings': bookings.count()
    })


    """
    Create new staff member.
    Accessible by managers and admins.
    """
    if not request.user.is_hotel_management():
        messages.error(request, 'Only hotel managers can create staff accounts.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            staff_user = form.save(commit=False)
            staff_user.is_staff = True
            staff_user.is_staff_active = True
            
            # Set permissions based on role
            if staff_user.role == 'manager':
                staff_user.can_manage_rooms = True
                staff_user.can_manage_bookings = True
                staff_user.can_process_payments = True
                staff_user.can_check_in_out = True
                staff_user.can_manage_staff = True
                staff_user.can_view_reports = True
            
            staff_user.save()
            
            # Create audit log
            try:
                from apps.core.models import AuditLog
                AuditLog.objects.create(
                    user=request.user,
                    action='staff_created',
                    description=f"Created {staff_user.get_role_display()} account for {staff_user.get_full_name()} ({staff_user.email})"
                )
            except:
                pass
            
            messages.success(
                request,
                f'✅ Staff account created! {staff_user.get_full_name()} can login with: {staff_user.email}'
            )
            return redirect('dashboard:staff_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'staff/users/create_staff.html', {
        'form': form,
        'title': 'Add New Staff Member'
    })
@login_required
def staff_create(request):
    """
    Create new staff member.
    Accessible by managers and admins.
    """
    if not request.user.is_hotel_management():
        messages.error(request, 'Only hotel managers can create staff accounts.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            try:
                staff_user = form.save(commit=False)
                staff_user.is_staff = True
                staff_user.is_staff_active = True
                staff_user.save()
                
                # Create audit log
                try:
                    from apps.core.models import AuditLog
                    AuditLog.objects.create(
                        user=request.user,
                        action='staff_created',
                        description=f"Created {staff_user.get_role_display()} account for {staff_user.get_full_name()} ({staff_user.email})"
                    )
                except:
                    pass
                
                messages.success(
                    request,
                    f'✅ Staff account created successfully! '
                    f'{staff_user.get_full_name()} can now login with: {staff_user.email}'
                )
                return redirect('dashboard:staff_list')
                
            except Exception as e:
                messages.error(request, f'Error creating staff: {str(e)}')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'staff/users/create_staff.html', {
        'form': form,
        'title': 'Add New Staff Member'
    })

@login_required
@staff_required
def staff_list(request):
    """
    List all staff members.
    """
    staff_users = User.objects.filter(
        role__in=['staff', 'manager']
    ).order_by('role', '-date_joined')
    
    # Count stats
    total = staff_users.count()
    active_count = staff_users.filter(is_staff_active=True).count()
    inactive_count = total - active_count
    
    return render(request, 'staff/users/staff_list.html', {
        'staff_users': staff_users,
        'total_staff': total,
        'active_count': active_count,
        'inactive_count': inactive_count,
    })


@login_required
@staff_required
def staff_detail(request, pk):
    """
    View staff member details.
    """
    staff_user = get_object_or_404(
        User.objects.filter(role__in=['staff', 'manager']),
        pk=pk
    )
    
    # Get their processed bookings
    processed_bookings = staff_user.processed_bookings.select_related(
        'guest', 'room'
    ).order_by('-created_at')[:20]
    
    return render(request, 'staff/users/staff_detail.html', {
        'staff_user': staff_user,
        'processed_bookings': processed_bookings,
        'total_processed': staff_user.processed_bookings.count(),
    })


@login_required
def staff_edit(request, pk):
    """
    Edit staff member.
    Only accessible by managers and admins.
    """
    if not request.user.is_hotel_management():
        messages.error(request, 'Only hotel managers can edit staff accounts.')
        return redirect('dashboard:index')
    
    staff_user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        staff_user.first_name = request.POST.get('first_name', staff_user.first_name)
        staff_user.last_name = request.POST.get('last_name', staff_user.last_name)
        staff_user.phone = request.POST.get('phone', staff_user.phone)
        staff_user.position = request.POST.get('position', staff_user.position)
        staff_user.department = request.POST.get('department', staff_user.department)
        
        # Permissions
        staff_user.can_manage_rooms = request.POST.get('can_manage_rooms') == 'on'
        staff_user.can_manage_bookings = request.POST.get('can_manage_bookings') == 'on'
        staff_user.can_process_payments = request.POST.get('can_process_payments') == 'on'
        staff_user.can_check_in_out = request.POST.get('can_check_in_out') == 'on'
        staff_user.can_view_reports = request.POST.get('can_view_reports') == 'on'
        staff_user.is_staff_active = request.POST.get('is_staff_active') == 'on'
        
        staff_user.save()
        messages.success(request, f'✅ {staff_user.get_full_name()} updated successfully.')
        return redirect('dashboard:staff_detail', pk=staff_user.pk)
    
    return render(request, 'staff/users/edit_staff.html', {
        'staff_user': staff_user
    })


@login_required
def staff_toggle(request, pk):
    """
    Activate/Deactivate staff account.
    Only accessible by managers and admins.
    """
    if not request.user.is_hotel_management():
        messages.error(request, 'Only hotel managers can manage staff accounts.')
        return redirect('dashboard:index')
    
    staff_user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        if staff_user.is_staff_active:
            reason = request.POST.get('reason', 'Deactivated by manager')
            staff_user.deactivate(reason)
            messages.warning(request, f'{staff_user.get_full_name()} has been deactivated.')
        else:
            staff_user.activate()
            messages.success(request, f'{staff_user.get_full_name()} has been reactivated.')
    
    return redirect('dashboard:staff_detail', pk=staff_user.pk)