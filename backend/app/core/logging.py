import sys
import re
from loguru import logger

# Regex patterns for sensitive data redaction
SENSITIVE_PATTERNS = [
    (r"(?i)bearer\s+[a-zA-Z0-9\-_.]+", "Bearer [REDACTED_TOKEN]"),
    (r"(?i)password[\"']?\s*[:=]\s*[\"']?[^\"',\s]+", 'password="[REDACTED]"'),
    (r"(?i)jwt_secret[\"']?\s*[:=]\s*[\"']?[^\"',\s]+", 'jwt_secret="[REDACTED]"'),
    (r"(?i)gemini_api_key[\"']?\s*[:=]\s*[\"']?[^\"',\s]+", 'gemini_api_key="[REDACTED]"'),
    (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
]


def phi_redaction_filter(record: dict) -> bool:
    """Filter interceptor to prevent sensitive PHI/PII leakage into logs."""
    msg = record["message"]
    for pattern, replacement in SENSITIVE_PATTERNS:
        msg = re.sub(pattern, replacement, msg)
    record["message"] = msg
    return True


def setup_logging(debug: bool = True) -> None:
    """Configure structured logging with Loguru."""
    logger.remove()
    log_level = "DEBUG" if debug else "INFO"
    
    logger.add(
        sys.stdout,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        filter=phi_redaction_filter,
        colorize=True,
    )
