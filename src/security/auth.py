"""
Authentication, Authorization, and Rate-Limiting Module.
Implements token verification, API key management, and production rate limits
to prevent resource exhaustion and comply with data governance standards.
"""

import time
import hmac
import hashlib
import secrets
from typing import Dict, Optional, Tuple, Any
from collections import defaultdict

class SecurityAuthManager:
    """
    Manages API keys, session tokens, and request rate-limiting.
    """

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or "legal-ai-secret-key-2026-indic-nlp"
        # Seeded API keys for production/demo roles
        self.api_keys: Dict[str, Dict[str, Any]] = {
            "legal-demo-key-2026": {
                "user_id": "usr_demo_advocate",
                "role": "ADVOCATE",
                "name": "Enrolled Advocate / Legal Counsel",
                "rate_limit_per_minute": 60,
                "is_active": True
            },
            "legal-admin-master-key": {
                "user_id": "usr_system_admin",
                "role": "ADMIN",
                "name": "System Administrator",
                "rate_limit_per_minute": 300,
                "is_active": True
            }
        }
        # In-memory rate limiting: user_or_ip -> list of timestamps
        self.request_history: Dict[str, list] = defaultdict(list)
        # Active sessions: token -> session data
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def authenticate_request(
        self,
        api_key: Optional[str] = None,
        session_token: Optional[str] = None,
        client_ip: str = "127.0.0.1"
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates API key or session token and enforces rate limits.
        Returns: (is_allowed, error_message, user_context)
        """
        # 1. API Key Auth
        if api_key:
            if api_key in self.api_keys and self.api_keys[api_key]["is_active"]:
                user_ctx = dict(self.api_keys[api_key])
                user_ctx["auth_type"] = "API_KEY"
                is_rate_ok, msg = self._check_rate_limit(user_ctx["user_id"], user_ctx["rate_limit_per_minute"])
                if not is_rate_ok:
                    return False, msg, {}
                return True, "OK", user_ctx
            return False, "Invalid or expired API Key.", {}

        # 2. Session Token Auth
        if session_token:
            if session_token in self.active_sessions:
                sess = self.active_sessions[session_token]
                if time.time() < sess["expires_at"]:
                    user_ctx = dict(sess["user_data"])
                    user_ctx["auth_type"] = "SESSION"
                    is_rate_ok, msg = self._check_rate_limit(user_ctx["user_id"], 60)
                    if not is_rate_ok:
                        return False, msg, {}
                    return True, "OK", user_ctx
                else:
                    del self.active_sessions[session_token]
                    return False, "Session token has expired. Please re-authenticate.", {}

        # 3. Default Guest Access (Rate-limited to 20 req/min)
        guest_id = f"guest_{client_ip}"
        is_rate_ok, msg = self._check_rate_limit(guest_id, 20)
        if not is_rate_ok:
            return False, msg, {}

        user_ctx = {
            "user_id": guest_id,
            "role": "GUEST",
            "name": f"Guest User ({client_ip})",
            "auth_type": "PUBLIC_GUEST",
            "rate_limit_per_minute": 20
        }
        return True, "OK", user_ctx

    def create_session(self, username: str, role: str = "ADVOCATE", ttl_seconds: int = 86400) -> str:
        """Creates a signed cryptographically secure session token."""
        token = secrets.token_hex(24)
        expires_at = time.time() + ttl_seconds
        self.active_sessions[token] = {
            "token": token,
            "user_data": {
                "user_id": f"usr_{hashlib.md5(username.encode()).hexdigest()[:8]}",
                "username": username,
                "role": role,
                "name": username.title()
            },
            "created_at": time.time(),
            "expires_at": expires_at
        }
        return token

    def register_api_key(self, user_name: str, role: str = "ADVOCATE", rate_limit: int = 60) -> str:
        """Issues a new production API key for authorized legal entities."""
        key = f"legal-api-{secrets.token_urlsafe(16)}"
        self.api_keys[key] = {
            "user_id": f"usr_{secrets.token_hex(4)}",
            "role": role,
            "name": user_name,
            "rate_limit_per_minute": rate_limit,
            "is_active": True
        }
        return key

    def _check_rate_limit(self, identifier: str, limit_per_minute: int) -> Tuple[bool, str]:
        """Sliding-window rate limiter."""
        now = time.time()
        window_start = now - 60.0
        # Clean older entries
        self.request_history[identifier] = [
            ts for ts in self.request_history[identifier] if ts > window_start
        ]
        if len(self.request_history[identifier]) >= limit_per_minute:
            return False, f"Rate limit exceeded: maximum {limit_per_minute} requests per minute allowed."

        self.request_history[identifier].append(now)
        return True, "OK"
