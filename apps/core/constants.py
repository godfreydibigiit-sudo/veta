"""
Constants for VETA Hotel Booking System.
"""

# Booking reference ID prefix
REFERENCE_PREFIX = 'VETA'

# Room types
ROOM_TYPES = [
    ('single', 'Single Room'),
    ('double', 'Double Room'),
    ('twin', 'Twin Room'),
    ('suite', 'Suite Room'),
    ('family', 'Family Room'),
    ('deluxe', 'Deluxe Room'),
]

# Room status choices
ROOM_STATUS = [
    ('available', 'Available'),
    ('occupied', 'Occupied'),
    ('maintenance', 'Maintenance'),
    ('reserved', 'Reserved'),
]

# Booking status choices
BOOKING_STATUS = [
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('checked_in', 'Checked In'),
    ('checked_out', 'Checked Out'),
    ('cancelled', 'Cancelled'),
]

# Payment status choices
PAYMENT_STATUS = [
    ('unpaid', 'Unpaid'),
    ('paid', 'Paid'),
    ('partial', 'Partially Paid'),
    ('refunded', 'Refunded'),
]

# User roles
USER_ROLES = [
    ('guest', 'Guest'),
    ('staff', 'Staff'),
    ('admin', 'Admin'),
]

# Currency
CURRENCY = 'TZS'
CURRENCY_SYMBOL = 'TZS'

# Pagination
ITEMS_PER_PAGE = 12
BOOKINGS_PER_PAGE = 10

# Date formats
DATE_FORMAT = '%d %b %Y'
DATETIME_FORMAT = '%d %b %Y %H:%M'

# Maximum advance booking days
MAX_ADVANCE_BOOKING_DAYS = 365

# Session keys
SESSION_CART_KEY = 'booking_cart'
SESSION_SEARCH_KEY = 'last_search_params'

# User roles
USER_ROLES = [
    ('guest', 'Guest'),
    ('staff', 'Staff'),
    ('manager', 'Hotel Manager'),
    ('admin', 'System Admin'),
]

# Staff role hierarchy (for permission inheritance)
ROLE_HIERARCHY = {
    'guest': 0,
    'staff': 1,
    'manager': 2,
    'admin': 3,
}

# Default staff permissions
DEFAULT_STAFF_PERMISSIONS = {
    'can_manage_rooms': False,
    'can_manage_bookings': True,
    'can_process_payments': False,
    'can_check_in_out': True,
    'can_manage_staff': False,
    'can_view_reports': False,
}

# Default manager permissions
DEFAULT_MANAGER_PERMISSIONS = {
    'can_manage_rooms': True,
    'can_manage_bookings': True,
    'can_process_payments': True,
    'can_check_in_out': True,
    'can_manage_staff': True,
    'can_view_reports': True,
}