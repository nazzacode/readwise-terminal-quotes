import os

# Get from https://readwise.io/access_token
READWISE_TOKEN = os.getenv('READWISE_TOKEN', '')

API_BASE = 'https://readwise.io/api/v2'
HIGHLIGHTS_ENDPOINT = f'{API_BASE}/highlights'

# Rate limit: 20 requests per minute for highlights
# Page size: 1-1000, default 20
DEFAULT_PAGE_SIZE = 1
MAX_RANDOM_PAGE = 1000