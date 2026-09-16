
"""
API Key authentication + request logging for Solar Fleet Intelligence.
"""
import os
import time
import logging
from fastapi import Header, HTTPException, Request
from datetime import datetime

# ---------- Logging Setup ----------
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('solar_api')

# ---------- API Keys ----------
VALID_API_KEYS = {
    "demo-key-tata-2026": "tata_demo_user",
    "test-key-local": "local_dev"
}


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Dependency — validates API key from request header."""
    if x_api_key not in VALID_API_KEYS:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return VALID_API_KEYS[x_api_key]


async def log_request(request: Request, call_next):
    """Middleware — logs every request with timing."""
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000

    logger.info(
        f"{request.method} {request.url.path} | "
        f"status={response.status_code} | "
        f"time={duration_ms:.1f}ms | "
        f"client={request.client.host if request.client else 'unknown'}"
    )
    return response