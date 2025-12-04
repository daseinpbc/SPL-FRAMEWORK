"""
Layer 0: Reactive Schemas (Validation)

Cost: $0
Speed: <1ms
Purpose: Fast, deterministic validation

Examples:
- Format validation (RFC 5322 for emails)
- Permission checks (user authorization)
- Rate limiting (quota enforcement)
- Blocklist/allowlist matching

Principle: Arkin's "reactive modules respond to immediate stimuli without deliberation"
"""

from typing import Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class ValidationResult:
    """Result from Layer 0 validation."""
    valid: bool
    reason: Optional[str] = None
    rejected: bool = False


class Layer0Reactive:
    """
    Layer 0: Reactive validation layer.
    
    Performs fast, deterministic validation before any expensive processing.
    All checks are free ($0 cost) and execute in <1ms.
    
    Attributes:
        min_length: Minimum content length
        max_length: Maximum content length
        blocklist: Set of blocked terms/patterns
        allowlist: Set of explicitly allowed terms
        rate_limits: Rate limit tracking per user
    """
    
    def __init__(
        self,
        min_length: int = 5,
        max_length: int = 1000,
        blocklist: Optional[Set[str]] = None,
        allowlist: Optional[Set[str]] = None,
    ):
        """
        Initialize Layer 0 with validation parameters.
        
        Args:
            min_length: Minimum allowed content length
            max_length: Maximum allowed content length
            blocklist: Terms that cause immediate rejection
            allowlist: Terms that bypass certain checks
        """
        self.min_length = min_length
        self.max_length = max_length
        self.blocklist = blocklist or set()
        self.allowlist = allowlist or set()
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self._validation_count = 0
        
    def validate(self, request: Dict[str, Any]) -> ValidationResult:
        """
        Validate a request through all reactive checks.
        
        Args:
            request: Dictionary with 'user_id' and 'content' keys
            
        Returns:
            ValidationResult indicating if request passed validation
        """
        self._validation_count += 1
        
        content = request.get('content', '')
        user_id = request.get('user_id', 'anonymous')
        
        # Check 1: Type validation
        if not isinstance(content, str):
            return ValidationResult(
                valid=False,
                reason='Content must be a string',
                rejected=True
            )
        
        # Check 2: Length validation
        if len(content) < self.min_length:
            return ValidationResult(
                valid=False,
                reason=f'Content too short (min {self.min_length} chars)',
                rejected=True
            )
            
        if len(content) > self.max_length:
            return ValidationResult(
                valid=False,
                reason=f'Content too long (max {self.max_length} chars)',
                rejected=True
            )
        
        # Check 3: Blocklist check
        content_lower = content.lower()
        for blocked in self.blocklist:
            if blocked.lower() in content_lower:
                return ValidationResult(
                    valid=False,
                    reason=f'Blocked term detected: {blocked}',
                    rejected=True
                )
        
        # Check 4: Rate limiting
        rate_result = self._check_rate_limit(user_id)
        if not rate_result.valid:
            return rate_result
        
        # All checks passed
        return ValidationResult(valid=True)
    
    def _check_rate_limit(
        self, 
        user_id: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> ValidationResult:
        """
        Check if user has exceeded rate limits.
        
        Args:
            user_id: Unique user identifier
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
            
        Returns:
            ValidationResult for rate limit check
        """
        now = datetime.now()
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = {
                'count': 1,
                'window_start': now
            }
            return ValidationResult(valid=True)
        
        user_limits = self.rate_limits[user_id]
        elapsed = (now - user_limits['window_start']).total_seconds()
        
        if elapsed > window_seconds:
            # Reset window
            self.rate_limits[user_id] = {
                'count': 1,
                'window_start': now
            }
            return ValidationResult(valid=True)
        
        if user_limits['count'] >= max_requests:
            return ValidationResult(
                valid=False,
                reason='Rate limit exceeded',
                rejected=True
            )
        
        user_limits['count'] += 1
        return ValidationResult(valid=True)
    
    def add_to_blocklist(self, term: str) -> None:
        """Add a term to the blocklist."""
        self.blocklist.add(term)
    
    def remove_from_blocklist(self, term: str) -> None:
        """Remove a term from the blocklist."""
        self.blocklist.discard(term)
    
    def add_to_allowlist(self, term: str) -> None:
        """Add a term to the allowlist."""
        self.allowlist.add(term)
    
    def reset_rate_limits(self) -> None:
        """Reset all rate limits."""
        self.rate_limits.clear()
    
    @property
    def validation_count(self) -> int:
        """Number of validations performed."""
        return self._validation_count
    
    def report(self) -> Dict[str, Any]:
        """Generate report for this layer."""
        return {
            'layer': 0,
            'name': 'reactive',
            'validations': self._validation_count,
            'blocklist_size': len(self.blocklist),
            'allowlist_size': len(self.allowlist),
            'active_rate_limits': len(self.rate_limits),
            'cost': 0.0,  # Layer 0 is always free
        }
