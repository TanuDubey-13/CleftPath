"""
Common FastAPI dependencies re-export.
"""

from app.db.session import get_db
from app.dependencies.auth import (
    check_document_ownership,
    check_patient_ownership,
    get_current_active_user,
    get_current_user,
    get_token_from_request,
    require_role,
)

__all__ = [
    "get_db",
    "get_token_from_request",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "check_patient_ownership",
    "check_document_ownership",
]
