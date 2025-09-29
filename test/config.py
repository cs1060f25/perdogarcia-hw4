"""
Configuration module for API testing

Author: Pedro Garcia
Handles environment detection and API URL configuration for testing
both local and deployed endpoints.

Auto-detects production environment based on:
1. Vercel environment variables (VERCEL_URL)
2. Netlify environment variables (URL)
3. Manual override via API_ENVIRONMENT
4. Fallback to local development
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def detect_environment():
    """
    Auto-detect the current environment.
    
    Returns:
        str: 'production' or 'local'
    """
    # First check for production platform environment variables (these take precedence)
    if os.getenv('VERCEL_URL'):  # Vercel deployment
        return 'production'
    elif os.getenv('URL') and 'netlify' in os.getenv('URL', ''):  # Netlify deployment
        return 'production'
    elif os.getenv('RENDER_EXTERNAL_URL'):  # Render deployment
        return 'production'
    elif os.getenv('RAILWAY_PUBLIC_DOMAIN'):  # Railway deployment
        return 'production'
    
    # Manual override from environment or .env file
    manual_env = os.getenv('API_ENVIRONMENT')
    if manual_env:
        return manual_env.lower()
    
    # Load .env file only if we're not in a detected production environment
    project_root = Path(__file__).parent.parent
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        manual_env = os.getenv('API_ENVIRONMENT')
        if manual_env:
            return manual_env.lower()
    
    # Default to local
    return 'local'

def get_api_base_url():
    """
    Get the API base URL based on the current environment.
    
    Returns:
        str: Base URL for the API (local or production)
    """
    environment = detect_environment()
    
    if environment == 'production':
        # Try to get production URL from various sources
        production_url = (
            os.getenv('PRODUCTION_API_URL') or  # Manual override
            os.getenv('VERCEL_URL') or          # Vercel auto-detection
            os.getenv('URL') or                 # Netlify auto-detection
            os.getenv('RENDER_EXTERNAL_URL') or # Render auto-detection
            os.getenv('RAILWAY_PUBLIC_DOMAIN')  # Railway auto-detection
        )
        
        if production_url:
            # Ensure it has https:// prefix
            if not production_url.startswith('http'):
                production_url = f"https://{production_url}"
            return production_url
        else:
            raise ValueError(
                "Production environment detected but no production URL found. "
                "Set PRODUCTION_API_URL environment variable."
            )
    else:
        # Local development
        return os.getenv('LOCAL_API_URL', 'http://localhost:5005')

def is_production_environment():
    """
    Check if we're in production environment.
    
    Returns:
        bool: True if production, False if local
    """
    return detect_environment() == 'production'

def get_environment_info():
    """
    Get information about the current environment.
    
    Returns:
        dict: Environment configuration details
    """
    environment = detect_environment()
    
    return {
        'environment': environment,
        'api_url': get_api_base_url(),
        'is_production': environment == 'production',
        'detected_platform': _detect_platform()
    }

def _detect_platform():
    """
    Detect which deployment platform we're running on.
    
    Returns:
        str: Platform name or 'local'
    """
    if os.getenv('VERCEL_URL'):
        return 'vercel'
    elif os.getenv('URL') and 'netlify' in os.getenv('URL', ''):
        return 'netlify'
    elif os.getenv('RENDER_EXTERNAL_URL'):
        return 'render'
    elif os.getenv('RAILWAY_PUBLIC_DOMAIN'):
        return 'railway'
    else:
        return 'local'
