"""
Layer 2: Deliberative (Foundation Model Reasoning)

Cost: $0.01+ per call
Speed: 100-500ms
Purpose: Complex reasoning for novel situations

Examples:
- Understanding nuanced context
- Reasoning about edge cases
- Pattern learning
- Complex analysis

Principle: Arkin's "deliberation only when reactive layers cannot decide"
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DeliberativeResult:
    """Result from foundation model reasoning."""
    category: str
    confidence: float
    cost: float
    reasoning: Optional[str] = None
    model: Optional[str] = None
    
    
class Layer2Deliberative:
    """
    Layer 2: Deliberative foundation model layer.
    
    Handles complex reasoning that Layers 0 and 1 cannot address.
    This layer interfaces with foundation models like Claude, GPT-4, etc.
    
    Attributes:
        model_client: Optional foundation model client
        cost_per_call: Cost per foundation model call
        default_confidence: Default confidence for simulated responses
    """
    
    def __init__(
        self,
        model_client: Optional[Any] = None,
        cost_per_call: float = 0.01,
        model_name: str = "simulated",
    ):
        """
        Initialize Layer 2.
        
        Args:
            model_client: Foundation model API client (e.g., Anthropic client)
            cost_per_call: Cost per API call in dollars
            model_name: Name of the model being used
        """
        self.model_client = model_client
        self.cost_per_call = cost_per_call
        self.model_name = model_name
        self._call_count = 0
        self._total_cost = 0.0
        
    def reason(self, content: str, context: Optional[Dict[str, Any]] = None) -> DeliberativeResult:
        """
        Use foundation model for reasoning.
        
        Args:
            content: Content to reason about
            context: Optional context for the request
            
        Returns:
            DeliberativeResult with category and confidence
        """
        self._call_count += 1
        self._total_cost += self.cost_per_call
        
        if self.model_client is not None:
            # Use actual foundation model
            return self._call_model(content, context)
        else:
            # Use simulated reasoning
            return self._simulated_reason(content)
    
    def _call_model(self, content: str, context: Optional[Dict[str, Any]] = None) -> DeliberativeResult:
        """
        Call the actual foundation model.
        
        This is a placeholder that should be overridden or the model_client
        should be configured to handle the actual API call.
        """
        # Default implementation - should be overridden by MCPClient
        return self._simulated_reason(content)
    
    def _simulated_reason(self, content: str) -> DeliberativeResult:
        """
        Simulated foundation model reasoning for demo/testing.
        
        Args:
            content: Content to classify
            
        Returns:
            DeliberativeResult with simulated classification
        """
        text_lower = content.lower()
        
        # Simulated LLM categorization logic
        if 'urgent' in text_lower or 'asap' in text_lower or 'emergency' in text_lower:
            return DeliberativeResult(
                category='urgent',
                confidence=0.92,
                cost=self.cost_per_call,
                reasoning='Contains urgency indicators',
                model=self.model_name,
            )
        elif 'invoice' in text_lower or 'billing' in text_lower or 'payment' in text_lower:
            return DeliberativeResult(
                category='billing',
                confidence=0.88,
                cost=self.cost_per_call,
                reasoning='Contains billing-related terms',
                model=self.model_name,
            )
        elif 'unsubscribe' in text_lower or 'viagra' in text_lower or 'lottery' in text_lower:
            return DeliberativeResult(
                category='spam',
                confidence=0.95,
                cost=self.cost_per_call,
                reasoning='Contains spam indicators',
                model=self.model_name,
            )
        else:
            return DeliberativeResult(
                category='other',
                confidence=0.75,
                cost=self.cost_per_call,
                reasoning='No specific category matched',
                model=self.model_name,
            )
    
    def set_model_client(self, client: Any) -> None:
        """Set or update the foundation model client."""
        self.model_client = client
    
    def set_cost_per_call(self, cost: float) -> None:
        """Set the cost per API call."""
        self.cost_per_call = cost
    
    @property
    def call_count(self) -> int:
        """Number of foundation model calls made."""
        return self._call_count
    
    @property
    def total_cost(self) -> float:
        """Total cost incurred by this layer."""
        return self._total_cost
    
    def reset_tracking(self) -> None:
        """Reset call count and cost tracking."""
        self._call_count = 0
        self._total_cost = 0.0
    
    def report(self) -> Dict[str, Any]:
        """Generate report for this layer."""
        return {
            'layer': 2,
            'name': 'deliberative',
            'model': self.model_name,
            'calls': self._call_count,
            'cost_per_call': self.cost_per_call,
            'total_cost': self._total_cost,
            'has_model_client': self.model_client is not None,
        }
