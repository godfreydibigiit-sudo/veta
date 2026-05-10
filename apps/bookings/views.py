"""
Views for booking management - guest and staff views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from apps.bookings.models import Booking
from apps.bookings.forms import (
    BookingCreateForm, 
    BookingStatusForm, 
    BookingSearchForm
)
from apps.bookings.services import BookingService
from apps.rooms.models import Room
from apps.core.decorators import staff_required, guest_required
from apps.core.constants import BOOKINGS_PER_PAGE
from django.db.models import Q


# ============= GUEST VIEWS =============

@login_required
@guest_required
def create_booking(request, room_id):
    """
    Guest creates a new booking for a specific room.
    """
    room = get_object_or_404(Room, pk=room_id, is_active=True)
    
    if request.method == 'POST':
        form = BookingCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    booking = BookingService.create_booking(
                        guest=request.user,
                        room=room,
                        check_in=form.cleaned_data['check_in'],
                        check_out=form.cleaned_data['check_out'],
                        guest_count=form.cleaned_data['guest_count'],
                        special_requests=form.cleaned_data.get('special_requests', '')
                    )
                
                messages.success(
                    request,
                    f'Booking created successfully! '
                    f'Your reference ID is {booking.reference_id}. '
                    f'Total: {booking.get_total_display()}'
                )
                return redirect('bookings:confirmation', reference_id=booking.reference_id)
            
            except ValueError as e:
                messages.error(request, str(e))
    else:
        # Pre-fill form if dates are in URL parameters
        initial = {}
        if 'check_in' in request.GET:
            initial['check_in'] = request.GET['check_in']
        if 'check_out' in request.GET:
            initial['check_out'] = request.GET['check_out']
        
        form = BookingCreateForm(initial=initial)
    
    context = {
        'form': form,
        'room': room,
    }
    
    return render(request, 'guest/bookings/create.html', context)


@login_required
@guest_required
def booking_confirmation(request, reference_id):
    """
    Display booking confirmation with reference ID.
    """
    booking = get_object_or_404(
        Booking.objects.select_related('guest', 'room'),
        reference_id=reference_id,
        guest=request.user
    )
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'guest/bookings/confirmation.html', context)


@login_required
@guest_required
def my_bookings(request):
    """
    Display guest's booking history.
    """
    bookings = request.user.bookings.select_related(
        'room'
    ).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter and status_filter != 'all':
        bookings = bookings.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(bookings, BOOKINGS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'bookings': page_obj,
        'status_filter': status_filter,
    }
    
    return render(request, 'guest/bookings/my_bookings.html', context)


@login_required
@guest_required
def booking_detail(request, reference_id):
    """
    Display booking details for guest.
    """
    booking = get_object_or_404(
        Booking.objects.select_related('guest', 'room', 'processed_by'),
        reference_id=reference_id
    )
    
    # Ensure guest can only view their own bookings
    if booking.guest != request.user and not request.user.is_staff_user():
        messages.error(request, 'You do not have permission to view this booking.')
        return redirect('bookings:my_bookings')
    
    context = {
        'booking': booking,
        'timeline': booking.get_timeline(),
    }
    
    return render(request, 'guest/bookings/detail.html', context)


@login_required
@guest_required
def cancel_booking(request, reference_id):
    """
    Guest cancels their booking.
    """
    booking = get_object_or_404(
        Booking,
        reference_id=reference_id,
        guest=request.user
    )
    
    if not booking.can_cancel:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bookings:detail', reference_id=reference_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Cancelled by guest')
        
        try:
            BookingService.cancel_booking(booking, reason, request.user)
            messages.success(
                request,
                f'Booking {booking.reference_id} has been cancelled.'
            )
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('bookings:my_bookings')
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'guest/bookings/cancel.html', context)


# ============= STAFF VIEWS =============

@login_required
@staff_required
def staff_booking_list(request):
    """
    Staff view: List all bookings with filters.
    """
    bookings = Booking.objects.select_related(
        'guest', 'room', 'processed_by'
    ).order_by('-created_at')
    
    # Apply filters
    form = BookingSearchForm(request.GET)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if query:
            bookings = BookingService.search_bookings(query)
        
        if status:
            bookings = bookings.filter(status=status)
        
        if date_from:
            bookings = bookings.filter(check_in__gte=date_from)
        
        if date_to:
            bookings = bookings.filter(check_out__lte=date_to)
    
    # Statistics
    stats = BookingService.get_booking_stats()
    
    # Pagination
    paginator = Paginator(bookings, BOOKINGS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'bookings': page_obj,
        'form': form,
        'stats': stats,
    }
    
    return render(request, 'staff/bookings/list.html', context)
@login_required
@staff_required
def staff_booking_detail(request, reference_id):
    """
    Staff view: View booking details.
    """
    from django.shortcuts import get_object_or_404
    
    booking = get_object_or_404(
        Booking.objects.select_related('guest', 'room', 'processed_by'),
        reference_id=reference_id
    )
    
    # Get all bookings by this guest
    guest_bookings = Booking.objects.filter(
        guest=booking.guest
    ).select_related('room').exclude(
        id=booking.id
    ).order_by('-created_at')[:5]
    
    context = {
        'booking': booking,
        'timeline': booking.get_timeline(),
        'guest_bookings': guest_bookings,
        'status_form': BookingStatusForm(),
    }
    
    return render(request, 'staff/bookings/detail.html', context)


@login_required
@staff_required
def staff_process_booking(request, reference_id):
    """
    Staff processes booking actions (approve, cancel, check-in, check-out, pay).
    """
    booking = get_object_or_404(Booking, reference_id=reference_id)
    
    if request.method == 'POST':
        form = BookingStatusForm(request.POST)
        
        if form.is_valid():
            action = form.cleaned_data['action']
            reason = form.cleaned_data.get('reason', '')
            
            try:
                with transaction.atomic():
                    if action == 'approve':
                        BookingService.approve_booking(booking, request.user)
                        messages.success(
                            request,
                            f'Booking {booking.reference_id} has been approved.'
                        )
                    
                    elif action == 'cancel':
                        BookingService.cancel_booking(
                            booking, reason, request.user
                        )
                        messages.success(
                            request,
                            f'Booking {booking.reference_id} has been cancelled.'
                        )
                    
                    elif action == 'mark_paid':
                        BookingService.process_payment(booking, request.user)
                        messages.success(
                            request,
                            f'Payment processed for booking {booking.reference_id}.'
                        )
                    
                    elif action == 'check_in':
                        BookingService.check_in(booking, request.user)
                        messages.success(
                            request,
                            f'Guest checked in successfully. '
                            f'Room {booking.room.room_number}.'
                        )
                    
                    elif action == 'check_out':
                        BookingService.check_out(booking, request.user)
                        messages.success(
                            request,
                            f'Guest checked out successfully. '
                            f'Room {booking.room.room_number} is now available.'
                        )
                
            except ValueError as e:
                messages.error(request, str(e))
        
        return redirect('bookings:staff_detail', reference_id=reference_id)
    
    return redirect('bookings:staff_list')


@login_required
@staff_required
def staff_search_guest(request):
    """
    Staff searches for guest by phone or reference ID.
    """
    query = request.GET.get('q', '')
    bookings = None
    guest = None
    
    if query:
        bookings = BookingService.search_bookings(query)
        
        if bookings.exists():
            guest = bookings.first().guest
        else:
            # Search guest directly
            from apps.users.models import User
            guest = User.objects.filter(
                Q(phone__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).filter(role='guest').first()
            
            if guest:
                bookings = guest.bookings.select_related('room').order_by('-created_at')
    
    context = {
        'query': query,
        'guest': guest,
        'bookings': bookings[:10] if bookings else None,
        'total_bookings': bookings.count() if bookings else 0,
    }
    
    return render(request, 'staff/bookings/search_guest.html', context)


@login_required
@staff_required
def staff_today_checkins(request):
    """
    Staff view: Today's expected check-ins.
    """
    today = timezone.now().date()
    
    checkins = Booking.objects.filter(
        check_in=today,
        status__in=['approved', 'pending']
    ).select_related('guest', 'room').order_by('created_at')
    
    context = {
        'checkins': checkins,
        'today': today,
        'total_expected': checkins.count(),
    }
    
    return render(request, 'staff/bookings/today_checkins.html', context)


@login_required
@staff_required
def staff_today_checkouts(request):
    """
    Staff view: Today's expected check-outs.
    """
    today = timezone.now().date()
    
    checkouts = Booking.objects.filter(
        check_out=today,
        status='checked_in'
    ).select_related('guest', 'room').order_by('room__room_number')
    
    context = {
        'checkouts': checkouts,
        'today': today,
        'total_expected': checkouts.count(),
    }
    
    return render(request, 'staff/bookings/today_checkouts.html', context)