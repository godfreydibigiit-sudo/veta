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
        if user.is_staff_user():
            return reverse_lazy('dashboard:index')
        return reverse_lazy('home')
    
    def form_valid(self, form):
        """Record login information."""
        response = super().form_valid(form)
        user = self.request.user
        
        # Record login details
        user.record_login(
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        
        messages.success(
            self.request,
            f'Welcome back, {user.first_name}!'
        )
        return response
    
    
    def get_success_url(self):
        """Redirect based on user role."""
        user = self.request.user
        if user.is_staff_user():
            return reverse_lazy('dashboard:index')
        return reverse_lazy('home')
    
    def form_valid(self, form):
        """Record login information."""
        response = super().form_valid(form)
        user = self.request.user
        
        # Record login details
        user.record_login(
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        
        messages.success(
            self.request,
            f'Welcome back, {user.first_name}!'
        )
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
@staff_required
def staff_create(request):
    """Admin creates staff account."""
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            staff_user = form.save()
            messages.success(
                request,
                f'Staff account created for {staff_user.get_full_name()}. '
                f'Login credentials sent to {staff_user.email}.'
            )
            return redirect('dashboard:staff_list')
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'staff/users/create_staff.html', {
        'form': form,
        'title': 'Create Staff Account'
    })


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