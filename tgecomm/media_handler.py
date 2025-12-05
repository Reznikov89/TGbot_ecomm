"""
Media handling utilities for TGecomm
"""
from typing import Optional, Dict, Any
from .logger import setup_logger

logger = setup_logger(__name__)


def get_media_type(media: Any) -> str:
    """Get human-readable media type name
    
    Args:
        media: Telegram media object
        
    Returns:
        str: Media type name
    """
    if media is None:
        return "None"
    
    # Get type name and convert to readable format
    type_name = type(media).__name__
    
    # Map common media types to readable names
    type_mapping: Dict[str, str] = {
        'MessageMediaPhoto': 'Photo',
        'MessageMediaDocument': 'Document',
        'MessageMediaVideo': 'Video',
        'MessageMediaAudio': 'Audio',
        'MessageMediaVoice': 'Voice',
        'MessageMediaSticker': 'Sticker',
        'MessageMediaContact': 'Contact',
        'MessageMediaGeo': 'Location',
        'MessageMediaVenue': 'Venue',
        'MessageMediaGame': 'Game',
        'MessageMediaPoll': 'Poll',
        'MessageMediaWebPage': 'WebPage'
    }
    
    return type_mapping.get(type_name, type_name)


def format_media_info(media: Any) -> str:
    """Format media information for display
    
    Args:
        media: Telegram media object
    
    Returns:
        str: Formatted media information string
    """
    if media is None:
        return ""
    
    media_type = get_media_type(media)
    info_parts = [f"[Media: {media_type}]"]
    
    if hasattr(media, 'document') and media.document:
        doc = media.document
        if hasattr(doc, 'size'):
            size_mb = doc.size / (1024 * 1024)
            info_parts.append(f"Size: {size_mb:.2f} MB")
        if hasattr(doc, 'mime_type'):
            info_parts.append(f"Type: {doc.mime_type}")
    
    return " ".join(info_parts)
