"""
Admin configuration for rooms app.
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.rooms.models import Room, RoomType, RoomImage


class RoomImageInline(admin.TabularInline):
    """Inline admin for room images."""
    model = RoomImage
    extra = 1
    fields = ['image', 'caption', 'order']


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    """Admin for room types."""
    
    list_display = ['name', 'code', 'base_capacity', 'max_capacity']
    list_filter = ['base_capacity']
    search_fields = ['name', 'code']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin for rooms."""
    
    # Include BOTH 'status' (for editing) AND 'status_display' (for colored badge)
    list_display = [
        'room_number', 'room_type', 'floor', 'price_display',
        'capacity', 'status', 'status_display', 'is_active'
    ]
    
    list_filter = [
        'room_type', 'floor', 'status', 'is_active'
    ]
    
    search_fields = ['room_number', 'description']
    
    # Now 'status' is in list_display, so list_editable works
    list_editable = ['status', 'is_active']
    
    inlines = [RoomImageInline]
    
    fieldsets = (
        ('Room Information', {
            'fields': ('room_number', 'room_type', 'floor', 'capacity')
        }),
        ('Pricing', {
            'fields': ('price_per_night',)
        }),
        ('Details', {
            'fields': ('description', 'image')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'notes')
        }),
    )
    
    def price_display(self, obj):
        """Display price with TZS currency and commas."""
        try:
            price = int(obj.price_per_night) if obj.price_per_night else 0
            return format_html(
                '<strong style="color: #2d7a2a;">TZS {}</strong>',
                f"{price:,}"
            )
        except (ValueError, TypeError):
            return format_html(
                '<strong style="color: #2d7a2a;">TZS 0</strong>'
            )
    price_display.short_description = 'Price/Night'
    price_display.admin_order_field = 'price_per_night'
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'available': 'green',
            'occupied': 'red',
            'maintenance': 'orange',
            'reserved': 'blue',
        }
        color = colors.get(obj.status, 'gray')
        status_text = obj.get_status_display()
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color,
            status_text
        )
    status_display.short_description = 'Status Color'
    status_display.admin_order_field = 'status'


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    """Admin for room images."""
    
    list_display = ['room', 'caption', 'order', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['room__room_number', 'caption']