"""
User Display Utilities for Backend
Generates unique 5-character identifiers for users throughout the platform
"""

def generate_unique_user_display(user_id: str) -> str:
    """
    Generates a unique 5-character identifier from a user ID
    Uses the first 5 characters of the user ID for consistency
    
    Args:
        user_id: The full user ID
        
    Returns:
        A 5-character unique identifier
    """
    if not user_id or not isinstance(user_id, str):
        return 'USER1'  # Fallback for invalid IDs
    
    # Take first 5 characters and convert to uppercase for consistency
    unique_id = user_id[:5].upper()
    
    # Ensure we always have 5 characters by padding with numbers if needed
    if len(unique_id) < 5:
        padding = '12345'[:5 - len(unique_id)]
        return unique_id + padding
    
    return unique_id

def get_user_display_name(user) -> str:
    """
    Gets display name for a user - always returns the unique 5-char identifier
    
    Args:
        user: User object with id attribute
        
    Returns:
        The unique 5-character identifier
    """
    return generate_unique_user_display(str(user.id))

def get_user_initials(user) -> str:
    """
    Gets initials for avatar display - uses the unique identifier
    
    Args:
        user: User object with id attribute
        
    Returns:
        2-character initials from the unique identifier
    """
    unique_id = generate_unique_user_display(str(user.id))
    return unique_id[:2]

def format_user_for_api(user) -> dict:
    """
    Formats user data for API responses with unique identifier
    
    Args:
        user: User database object
        
    Returns:
        Dictionary with user data using unique identifier
    """
    return {
        'id': str(user.id),
        'display_name': get_user_display_name(user),
        'initials': get_user_initials(user),
        'email': user.email,
        'is_active': user.is_active,
        'is_verified': user.is_verified,
        'role': user.role,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }