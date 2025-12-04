"""
SPL Agent - Main SPL Agent Orchestrator

Coordinates all three layers of the SPL architecture:
- Layer 0: Reactive (Validation)
- Layer 1: Tactical (Pattern Matching)
- Layer 2: Deliberative (Foundation Model)
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from .layer0_reactive import Layer0Reactive, ValidationResult
from .layer1_tactical import Layer1Tactical, PatternMatchResult
from .layer2_deliberative import Layer2Deliberative, DeliberativeResult
from .cost_tracker import CostTracker


@dataclass
class Decision:
    """
    Represents a decision made by the SPL pipeline.
    
    Attributes:
        category: The assigned category (e.g., 'urgent', 'billing', 'spam')
        method: How decision was made ('rule', 'pattern', 'llm')
        confidence: 0.0-1.0 confidence in this decision
        cost: Cost in dollars for this decision
        layer: Which layer made the decision (0, 1, or 2)
        suppressed: Whether an expensive layer was suppressed
    """
    category: str
    method: str
    confidence: float
    cost: float
    layer: int
    suppressed: bool = False


class SPLAgent:
    """
    Main SPL Agent that orchestrates all three layers.
    
    Processes requests through a hierarchical architecture:
    1. Layer 0: Validation (free, fast)
    2. Layer 1: Pattern matching (cheap, medium speed)
    3. Layer 2: Foundation model reasoning (expensive, slow)
    
    Lower layers can suppress upper layers, preventing expensive
    foundation model calls before they occur.
    
    Attributes:
        agent_id: Unique identifier for this agent
        layer0: Layer 0 (Reactive) instance
        layer1: Layer 1 (Tactical) instance
        layer2: Layer 2 (Deliberative) instance
        shared_state: Reference to network-wide shared state
        cost_tracker: Cost monitoring and reporting
    """
    
    def __init__(
        self,
        agent_id: str = "spl_agent",
        shared_state: Optional[Dict[str, Any]] = None,
        confidence_threshold: float = 0.85,
    ):
        """
        Initialize SPL Agent.
        
        Args:
            agent_id: Unique identifier for this agent
            shared_state: Reference to shared state for multi-agent coordination
            confidence_threshold: Minimum confidence to suppress Layer 2
        """
        self.agent_id = agent_id
        self.shared_state = shared_state or {}
        self.confidence_threshold = confidence_threshold
        
        # Initialize layers
        self.layer0 = Layer0Reactive()
        self.layer1 = Layer1Tactical(
            confidence_threshold=confidence_threshold,
            shared_state=self.shared_state,
        )
        self.layer2 = Layer2Deliberative()
        
        # Cost tracking
        self.cost_tracker = CostTracker()
        self._suppression_count = 0
    
    def process(self, request: Dict[str, Any]) -> Decision:
        """
        Process a request through all three layers.
        
        Args:
            request: Dictionary with 'user_id' and 'content' keys
            
        Returns:
            Decision with category, confidence, cost, and layer
            
        Execution flow:
        1. Layer 0: Validate structure
           - If invalid → return REJECTED
        
        2. Layer 1: Try pattern matching
           - If high confidence match → return PATTERN MATCH (skip Layer 2)
        
        3. Layer 2: Call foundation model
           - Learn new patterns from result
           - Return foundation model decision
        """
        content = request.get('content', '')
        user_id = request.get('user_id', 'anonymous')
        
        try:
            # ===== LAYER 0: VALIDATION =====
            validation = self.layer0.validate(request)
            if not validation.valid:
                decision = Decision(
                    category='REJECTED',
                    method='validation',
                    confidence=1.0,
                    cost=0.0,
                    layer=0,
                    suppressed=True,
                )
                self.cost_tracker.record_result(decision)
                return decision
            
            # ===== LAYER 1: PATTERN MATCHING =====
            match_result = self.layer1.match(content)
            if match_result is not None and match_result.matched:
                self._suppression_count += 1
                decision = Decision(
                    category=match_result.category or 'unknown',
                    method=match_result.method,
                    confidence=match_result.confidence,
                    cost=0.0,  # Pattern matching is free
                    layer=1,
                    suppressed=True,
                )
                self.cost_tracker.record_result(decision)
                return decision
            
            # ===== LAYER 2: FOUNDATION MODEL =====
            fm_result = self.layer2.reason(content)
            
            # Learn pattern if high confidence
            if fm_result.confidence >= 0.90:
                self.layer1.learn_pattern(
                    content=content,
                    category=fm_result.category,
                    confidence=fm_result.confidence,
                    learned_by=self.agent_id,
                )
            
            decision = Decision(
                category=fm_result.category,
                method='llm',
                confidence=fm_result.confidence,
                cost=fm_result.cost,
                layer=2,
                suppressed=False,
            )
            self.cost_tracker.record_result(decision)
            return decision
            
        except Exception as e:
            # Error handling: graceful degradation
            decision = Decision(
                category='ERROR',
                method='error_handler',
                confidence=0.0,
                cost=0.0,
                layer=0,
            )
            self.cost_tracker.record_result(decision)
            return decision
    
    def add_pattern(
        self,
        name: str,
        regex: str,
        category: str,
        confidence: float = 0.90,
    ) -> None:
        """
        Add a pattern to Layer 1.
        
        Args:
            name: Unique name for the pattern
            regex: Regular expression to match
            category: Category to assign if matched
            confidence: Confidence score (0.0-1.0)
        """
        self.layer1.add_pattern(name, regex, category, confidence)
    
    def add_to_blocklist(self, term: str) -> None:
        """Add a term to Layer 0 blocklist."""
        self.layer0.add_to_blocklist(term)
    
    def set_layer2(self, layer2: Any) -> None:
        """
        Set or replace Layer 2 (foundation model layer).
        
        Args:
            layer2: New Layer 2 instance (e.g., MCPClient)
        """
        self.layer2 = layer2
    
    @property
    def suppression_count(self) -> int:
        """Number of times Layer 2 was suppressed."""
        return self._suppression_count
    
    @property
    def patterns_learned(self) -> int:
        """Number of patterns learned."""
        return self.layer1.pattern_count
    
    def report(self) -> Dict[str, Any]:
        """
        Generate performance report for this agent.
        
        Returns:
            Dictionary with agent performance metrics
        """
        cost_report = self.cost_tracker.report()
        
        return {
            'agent_id': self.agent_id,
            'total_cost': cost_report['total_cost'],
            'cost_savings': cost_report['cost_savings'],
            'cost_reduction_factor': cost_report['cost_reduction_factor'],
            'suppression_rate': cost_report['suppression_rate'],
            'suppressions': self._suppression_count,
            'patterns_learned': self.patterns_learned,
            'layer_breakdown': cost_report['layer_breakdown'],
            'layer_reports': {
                'layer_0': self.layer0.report(),
                'layer_1': self.layer1.report(),
                'layer_2': self.layer2.report(),
            },
        }
    
    def reset(self) -> None:
        """Reset agent state for fresh start."""
        self.cost_tracker.reset()
        self._suppression_count = 0
        self.layer1.clear_cache()
        self.layer0.reset_rate_limits()
