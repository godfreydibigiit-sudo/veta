"""
Views for user authentication and management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from apps.users.models import User
from apps.users.forms import (
    GuestRegistrationForm, 
    StaffRegistrationForm,
    UserLoginForm,
    UserProfileForm
)
from apps.core.decorators import staff_required, guest_required


class GuestRegisterView(CreateView):
    """Guest user registration view."""
    model = User
    form_class = GuestRegistrationForm
    template_name = 'guest/register.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        """Process valid form and log user in."""
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            f'Welcome to VETA Hotel, {self.object.first_name}! '
            'Your account has been created successfully.'
        )
        return response
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect if user is already logged in."""
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class UserLoginView(LoginView):
    """Custom login view for all users."""
    form_class = UserLoginForm
    template_name = 'guest/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect based on user role."""
        user = self.request.user
        
        # Managers go to manager dashboard
        if user.is_manager():
            return reverse_lazy('dashboard:manager_index')
        
        # Staff and admins go to staff dashboard
        if user.is_staff_user():
            return reverse_lazy('dashboard:index')
        
        # Guests go to home
        return reverse_lazy('home')
    
    def form_valid(self, form):
        """Record login information."""
        response = super().form_valid(form)
        user = self.request.user
        user.record_login(ip_address=self.request.META.get('REMOTE_ADDR'))
        messages.success(self.request, f'Welcome back, {user.first_name}!')
        return response


@login_required
def user_logout(request):
    """Logout user and redirect to home."""
    user = request.user
    logout(request)
    messages.info(
        request,
        'You have been logged out successfully. Have a great day!'
    )
    return redirect('home')


@login_required
def staff_create(request):
    """
    Create new staff member.
    Only accessible by managers and admins.
    """
    # Check if user can manage staff
    if not request.user.is_hotel_management():
        messages.error(request, 'Only hotel managers can create staff accounts.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            staff_user = form.save(commit=False)
            staff_user.role = form.cleaned_data.get('role', 'staff')
            staff_user.is_staff = True
            staff_user.is_staff_active = True
            
            # Set default permissions based on role
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
                f'Staff account created successfully! '
                f'{staff_user.get_full_name()} can now login with email: {staff_user.email}'
            )
            return redirect('dashboard:staff_list')
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'staff/users/create_staff.html', {
        'form': form,
        'title': 'Create Staff Account'
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
    
    return render(request, 'staff/users/staff_list.html', {
        'staff_users': staff_users,
        'total_staff': staff_users.count()
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
    processed_bookings = staff_user.processed_bookings.select_related('guest', 'room').order_by('-created_at')[:20]
    
    return render(request, 'staff/users/staff_detail.html', {
        'staff_user': staff_user,
        'processed_bookings': processed_bookings
    })


@login_required
def staff_edit(request, pk):
    """
    Edit staff member permissions.
    Only accessible by managers and admins.
    """
    if not request.user.is_hotel_management():
        messages.error(request, 'Only hotel managers can edit staff accounts.')
        return redirect('dashboard:index')
    
    staff_user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Update permissions
        staff_user.position = request.POST.get('position', staff_user.position)
        staff_user.department = request.POST.get('department', staff_user.department)
        staff_user.can_manage_rooms = request.POST.get('can_manage_rooms') == 'on'
        staff_user.can_manage_bookings = request.POST.get('can_manage_bookings') == 'on'
        staff_user.can_process_payments = request.POST.get('can_process_payments') == 'on'
        staff_user.can_check_in_out = request.POST.get('can_check_in_out') == 'on'
        staff_user.can_view_reports = request.POST.get('can_view_reports') == 'on'
        staff_user.is_staff_active = request.POST.get('is_staff_active') == 'on'
        staff_user.save()
        
        messages.success(request, f'{staff_user.get_full_name()}\'s account updated successfully.')
        return redirect('dashboard:staff_list')
    
    return render(request, 'staff/users/edit_staff.html', {
        'staff_user': staff_user
    })


@login_required
def staff_toggle_active(request, pk):
    """
    Activate or deactivate a staff account.
    Only accessible by managers and admins.
    """
    if not request.user.is_hotel_management():
        messages.error(request, 'Only hotel managers can manage staff accounts.')
        return redirect('dashboard:index')
    
    staff_user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        if staff_user.is_staff_active:
            staff_user.deactivate(reason)
            messages.warning(request, f'{staff_user.get_full_name()}\'s account has been deactivated.')
        else:
            staff_user.activate()
            messages.success(request, f'{staff_user.get_full_name()}\'s account has been reactivated.')
    
    return redirect('dashboard:staff_detail', pk=staff_user.pk)


@login_required
def profile_view(request):
    """View user profile."""
    return render(request, 'guest/profile/view.html', {
        'user': request.user
    })


@login_required
def profile_edit(request):
    """Edit user profile."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'guest/profile/edit.html', {
        'form': form
    })


@login_required
@staff_required
def staff_list(request):
    """List all staff members."""
    staff_users = User.objects.filter(
        role__in=['staff', 'admin']
    ).select_related('staff_profile').order_by('-created_at')
    
    return render(request, 'staff/users/staff_list.html', {
        'staff_users': staff_users,
        'total_staff': staff_users.count()
    })


@login_required
@staff_required
def guest_list(request):
    """List all registered guests."""
    guests = User.objects.filter(
        role='guest'
    ).order_by('-created_at')
    
    return render(request, 'staff/users/guest_list.html', {
        'guests': guests,
        'total_guests': guests.count()
    })


@login_required
@staff_required
def user_detail(request, pk):
    """View user details."""
    user = get_object_or_404(
        User.objects.select_related('staff_profile'),
        pk=pk
    )
    
    # Get user's booking history
    bookings = user.bookings.select_related('room').order_by('-created_at')
    
    return render(request, 'staff/users/user_detail.html', {
        'user_profile': user,
        'bookings': bookings[:10],  # Last 10 bookings
        'total_bookings': bookings.count()
    })