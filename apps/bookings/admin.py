"""
Admin configuration for bookings app.
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin for bookings."""
    
    list_display = [
        'reference_id', 'guest_info', 'room_info', 'dates_display',
        'amount_display', 'status_badge', 'payment_badge'
    ]
    
    list_filter = [
        'status', 'payment_status', 'check_in', 'check_out'
    ]
    
    search_fields = [
        'reference_id', 'guest__email', 'guest__phone',
        'guest__first_name', 'guest__last_name', 'room__room_number'
    ]
    
    readonly_fields = [
        'reference_id', 'price_per_night', 'total_amount', 
        'nights', 'created_at', 'updated_at',
        'approved_at', 'cancelled_at', 'checked_in_at', 
        'checked_out_at', 'paid_at'
    ]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('reference_id', 'guest', 'room', 'guest_count')
        }),
        ('Dates', {
            'fields': ('check_in', 'check_out', 'nights')
        }),
        ('Financial', {
            'fields': ('price_per_night', 'total_amount', 'payment_status')
        }),
        ('Status', {
            'fields': ('status', 'processed_by')
        }),
        ('Timestamps', {
            'fields': (
                'approved_at', 'paid_at', 'checked_in_at',
                'checked_out_at', 'cancelled_at',
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'staff_notes', 'cancellation_reason')
        }),
    )
    
    def guest_info(self, obj):
        """Display guest name and phone."""
        name = obj.guest.get_full_name() if obj.guest else 'N/A'
        phone = obj.guest.phone if obj.guest else ''
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            name, phone
        )
    guest_info.short_description = 'Guest'
    guest_info.admin_order_field = 'guest__first_name'
    
    def room_info(self, obj):
        """Display room info."""
        if obj.room:
            return format_html(
                '<strong>Room {}</strong><br><small>{}</small>',
                obj.room.room_number,
                obj.room.get_room_type_display()
            )
        return 'N/A'
    room_info.short_description = 'Room'
    room_info.admin_order_field = 'room__room_number'
    
    def dates_display(self, obj):
        """Display check-in/out dates."""
        check_in = obj.check_in.strftime('%d %b %Y') if obj.check_in else ''
        check_out = obj.check_out.strftime('%d %b %Y') if obj.check_out else ''
        return format_html(
            '<span style="color: green;">In:</span> {}<br>'
            '<span style="color: red;">Out:</span> {}',
            check_in, check_out
        )
    dates_display.short_description = 'Dates'
    
    def amount_display(self, obj):
        """Display total amount with commas."""
        try:
            amount = int(obj.total_amount) if obj.total_amount else 0
            nights = obj.nights if obj.nights else 0
            return format_html(
                '<strong>TZS {}</strong><br><small>{} night(s)</small>',
                f"{amount:,}", nights
            )
        except (ValueError, TypeError):
            return format_html(
                '<strong>TZS 0</strong><br><small>0 night(s)</small>'
            )
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'total_amount'
    
    def status_badge(self, obj):
        """Display status with colored badge."""
        colors = {
            'pending': '#f0ad4e',
            'approved': '#5bc0de',
            'checked_in': '#337ab7',
            'checked_out': '#5cb85c',
            'cancelled': '#d9534f',
        }
        color = colors.get(obj.status, '#777')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def payment_badge(self, obj):
        """Display payment status with colored badge."""
        colors = {
            'unpaid': '#d9534f',
            'paid': '#5cb85c',
            'partial': '#f0ad4e',
            'refunded': '#5bc0de',
        }
        color = colors.get(obj.payment_status, '#777')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-size: 12px;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_badge.short_description = 'Payment'
    payment_badge.admin_order_field = 'payment_status'