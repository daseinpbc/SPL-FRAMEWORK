"""
Layer 1: Tactical Behaviors (Pattern Matching)

Cost: $0.001 per match
Speed: <10ms
Purpose: Match against learned patterns before foundation model

Examples:
- Regex patterns ("URGENT:" in email = urgent category)
- Classification rules (billing-related → billing category)
- Cache lookup (have we seen this before?)
- Business logic (if X then Y)

Principle: Arkin's "complex behaviors emerge from layered reactive primitives"
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import re


@dataclass
class Pattern:
    """A learned pattern for classification."""
    name: str
    regex: str
    category: str
    confidence: float
    learned_at: Optional[str] = None
    learned_by: Optional[str] = None
    match_count: int = 0


@dataclass
class PatternMatchResult:
    """Result from pattern matching."""
    matched: bool
    pattern_name: Optional[str] = None
    category: Optional[str] = None
    confidence: float = 0.0
    method: str = 'pattern'


class Layer1Tactical:
    """
    Layer 1: Tactical pattern matching layer.
    
    Matches requests against learned patterns to avoid expensive
    foundation model calls. Patterns can be added manually or
    learned from Layer 2 decisions.
    
    Attributes:
        patterns: Dictionary of registered patterns
        confidence_threshold: Minimum confidence to suppress Layer 2
        cache: Recent decision cache
        shared_state: Reference to network-wide shared state
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.85,
        shared_state: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Layer 1.
        
        Args:
            confidence_threshold: Minimum confidence to suppress Layer 2
            shared_state: Reference to shared state for multi-agent coordination
        """
        self.patterns: Dict[str, Pattern] = {}
        self.confidence_threshold = confidence_threshold
        self.shared_state = shared_state or {}
        self.cache: Dict[str, PatternMatchResult] = {}
        self._match_count = 0
        self._cost = 0.0
        
    def add_pattern(
        self,
        name: str,
        regex: str,
        category: str,
        confidence: float = 0.90,
    ) -> None:
        """
        Add a new pattern for matching.
        
        Args:
            name: Unique name for the pattern
            regex: Regular expression to match
            category: Category to assign if matched
            confidence: Confidence score (0.0-1.0)
        """
        self.patterns[name] = Pattern(
            name=name,
            regex=regex,
            category=category,
            confidence=confidence,
            learned_at=datetime.now().isoformat(),
        )
    
    def remove_pattern(self, name: str) -> bool:
        """
        Remove a pattern by name.
        
        Args:
            name: Pattern name to remove
            
        Returns:
            True if pattern was removed, False if not found
        """
        if name in self.patterns:
            del self.patterns[name]
            return True
        return False
    
    def match(self, content: str) -> Optional[PatternMatchResult]:
        """
        Try to match content against known patterns.
        
        Args:
            content: Text content to match
            
        Returns:
            PatternMatchResult if matched with sufficient confidence, None otherwise
        """
        self._match_count += 1
        content_lower = content.lower()
        
        # Check cache first (use SHA-256 for reliable cache keys)
        cache_key = hashlib.sha256(content_lower.encode()).hexdigest()
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            return cached if cached.matched else None
        
        # Strategy 1: Check local patterns
        for pattern_name, pattern in self.patterns.items():
            try:
                if re.search(pattern.regex, content_lower, re.IGNORECASE):
                    if pattern.confidence >= self.confidence_threshold:
                        pattern.match_count += 1
                        self._cost += 0.0001
                        result = PatternMatchResult(
                            matched=True,
                            pattern_name=pattern_name,
                            category=pattern.category,
                            confidence=pattern.confidence,
                            method='pattern_cached',
                        )
                        self.cache[cache_key] = result
                        return result
            except re.error:
                # Invalid regex, skip
                continue
        
        # Strategy 2: Check shared patterns from other agents
        if 'learned_patterns' in self.shared_state:
            for category, pattern_info in self.shared_state['learned_patterns'].items():
                if category.lower() in content_lower:
                    confidence = pattern_info.get('confidence', 0.0)
                    if confidence >= self.confidence_threshold:
                        self._cost += 0.0001
                        result = PatternMatchResult(
                            matched=True,
                            pattern_name=category,
                            category=category,
                            confidence=confidence,
                            method='pattern_shared',
                        )
                        self.cache[cache_key] = result
                        return result
        
        # No match found
        self.cache[cache_key] = PatternMatchResult(matched=False)
        return None
    
    def learn_pattern(
        self,
        content: str,
        category: str,
        confidence: float = 0.92,
        learned_by: Optional[str] = None,
    ) -> Optional[str]:
        """
        Learn a new pattern from content.
        
        Args:
            content: Content that was categorized
            category: Category assigned by Layer 2
            confidence: Confidence of the categorization
            learned_by: Agent ID that learned this pattern
            
        Returns:
            Name of the pattern if learned, None otherwise
        """
        if confidence < 0.90:
            return None
            
        # Extract key word from content
        words = content.lower().split()
        if not words:
            return None
            
        key_word = words[0]
        pattern_name = f"learned_{key_word}_{category}"
        
        # Store locally
        self.patterns[pattern_name] = Pattern(
            name=pattern_name,
            regex=key_word,
            category=category,
            confidence=confidence,
            learned_at=datetime.now().isoformat(),
            learned_by=learned_by,
        )
        
        # Share with network
        if 'learned_patterns' not in self.shared_state:
            self.shared_state['learned_patterns'] = {}
        
        self.shared_state['learned_patterns'][category] = {
            'confidence': confidence,
            'learned_by': learned_by,
            'learned_at': datetime.now().isoformat(),
        }
        
        return pattern_name
    
    def clear_cache(self) -> None:
        """Clear the pattern cache."""
        self.cache.clear()
    
    def list_patterns(self) -> List[Dict[str, Any]]:
        """List all registered patterns."""
        return [
            {
                'name': p.name,
                'regex': p.regex,
                'category': p.category,
                'confidence': p.confidence,
                'match_count': p.match_count,
            }
            for p in self.patterns.values()
        ]
    
    @property
    def pattern_count(self) -> int:
        """Number of registered patterns."""
        return len(self.patterns)
    
    @property
    def match_count(self) -> int:
        """Number of match attempts."""
        return self._match_count
    
    @property
    def cost(self) -> float:
        """Total cost incurred by this layer."""
        return self._cost
    
    def report(self) -> Dict[str, Any]:
        """Generate report for this layer."""
        return {
            'layer': 1,
            'name': 'tactical',
            'patterns': self.pattern_count,
            'match_attempts': self._match_count,
            'cache_size': len(self.cache),
            'cost': self._cost,
        }
