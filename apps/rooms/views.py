"""
Views for room management - both guest and staff views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from apps.rooms.models import Room
from apps.rooms.forms import RoomForm, RoomSearchForm
from apps.core.decorators import staff_required
from apps.core.constants import ITEMS_PER_PAGE


# ============= GUEST VIEWS =============

def room_list(request):
    """
    Display available rooms with search/filter functionality.
    """
    form = RoomSearchForm(request.GET or None)
    rooms = Room.objects.filter(is_active=True, status='available')
    
    if form.is_valid():
        check_in = form.cleaned_data.get('check_in')
        check_out = form.cleaned_data.get('check_out')
        room_type = form.cleaned_data.get('room_type')
        max_price = form.cleaned_data.get('max_price')
        
        if check_in and check_out:
            # Exclude rooms with conflicting bookings
            conflicting_room_ids = get_conflicting_room_ids(check_in, check_out)
            rooms = rooms.exclude(id__in=conflicting_room_ids)
        
        if room_type:
            rooms = rooms.filter(room_type=room_type)
        
        if max_price:
            rooms = rooms.filter(price_per_night__lte=max_price)
    else:
        # Default: show all available rooms without date filtering
        pass
    
    # Apply sorting
    sort_by = request.GET.get('sort', 'price_asc')
    if sort_by == 'price_asc':
        rooms = rooms.order_by('price_per_night')
    elif sort_by == 'price_desc':
        rooms = rooms.order_by('-price_per_night')
    elif sort_by == 'capacity':
        rooms = rooms.order_by('-capacity')
    
    # Pagination
    paginator = Paginator(rooms, ITEMS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'rooms': page_obj,
        'form': form,
        'total_rooms': rooms.count(),
        'current_sort': sort_by,
    }
    
    return render(request, 'guest/rooms/browse.html', context)


def room_detail(request, pk):
    """
    Display room details.
    """
    room = get_object_or_404(
        Room.objects.filter(is_active=True),
        pk=pk
    )
    
    # Get room images
    room_images = room.images.all().order_by('order')
    
    context = {
        'room': room,
        'room_images': room_images,
    }
    
    return render(request, 'guest/rooms/detail.html', context)


# ============= STAFF VIEWS =============

@login_required
@staff_required
def staff_room_list(request):
    """
    Staff view: List all rooms with management options.
    """
    rooms = Room.objects.filter(is_active=True).order_by('floor', 'room_number')
    
    # Statistics
    stats = {
        'total': rooms.count(),
        'available': rooms.filter(status='available').count(),
        'occupied': rooms.filter(status='occupied').count(),
        'maintenance': rooms.filter(status='maintenance').count(),
    }
    
    context = {
        'rooms': rooms,
        'stats': stats,
    }
    
    return render(request, 'staff/rooms/list.html', context)


@login_required
@staff_required
def staff_room_add(request):
    """
    Staff view: Add new room.
    """
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            messages.success(
                request,
                f'Room {room.room_number} added successfully.'
            )
            return redirect('rooms:staff_list')
    else:
        form = RoomForm()
    
    context = {
        'form': form,
        'title': 'Add New Room',
        'action': 'Add Room'
    }
    
    return render(request, 'staff/rooms/form.html', context)


@login_required
@staff_required
def staff_room_edit(request, pk):
    """
    Staff view: Edit existing room.
    """
    room = get_object_or_404(Room, pk=pk)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(
                request,
                f'Room {room.room_number} updated successfully.'
            )
            return redirect('rooms:staff_list')
    else:
        form = RoomForm(instance=room)
    
    context = {
        'form': form,
        'title': f'Edit Room {room.room_number}',
        'action': 'Update Room',
        'room': room
    }
    
    return render(request, 'staff/rooms/form.html', context)


@login_required
@staff_required
def staff_room_delete(request, pk):
    """
    Staff view: Soft delete room.
    """
    room = get_object_or_404(Room, pk=pk)
    
    if request.method == 'POST':
        # Check if room has active bookings
        active_bookings = room.bookings.filter(
            status__in=['approved', 'checked_in']
        ).exists()
        
        if active_bookings:
            messages.error(
                request,
                f'Cannot delete Room {room.room_number}. It has active bookings.'
            )
        else:
            room.soft_delete()
            messages.success(
                request,
                f'Room {room.room_number} has been removed.'
            )
        return redirect('rooms:staff_list')
    
    context = {
        'room': room
    }
    
    return render(request, 'staff/rooms/delete.html', context)


@login_required
@staff_required
def staff_room_toggle_status(request, pk):
    """
    Staff view: Toggle room status (AJAX recommended).
    """
    room = get_object_or_404(Room, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status in ['available', 'occupied', 'maintenance']:
            if room.update_status(new_status):
                messages.success(
                    request,
                    f'Room {room.room_number} status updated to {room.get_status_display()}.'
                )
            else:
                messages.error(
                    request,
                    f'Cannot change status from {room.get_status_display()} to {new_status}.'
                )
        else:
            messages.error(request, 'Invalid status.')
    
    return redirect('rooms:staff_list')


# ============= HELPER FUNCTIONS =============

def get_conflicting_room_ids(check_in, check_out):
    """
    Get IDs of rooms with conflicting bookings.
    """
    from apps.bookings.models import Booking
    
    bookings = Booking.objects.filter(
        Q(status__in=['pending', 'approved', 'checked_in']) &
        Q(check_in__lt=check_out) &
        Q(check_out__gt=check_in)
    ).values_list('room_id', flat=True)
    
    return list(bookings)