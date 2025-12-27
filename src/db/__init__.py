"""
PRIMAX Database Module
Supabase pgvector integration with async support

© 2025 Bakery Street Project
WATERMARK: PRIMAX-AI-BSP-2025
"""

from .supabase_client import SupabaseVectorClient, get_client

__all__ = ['SupabaseVectorClient', 'get_client']
