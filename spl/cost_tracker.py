"""
Cost Tracker - Cost Monitoring & Reporting

Tracks costs across all layers and provides detailed reporting
for cost optimization and analysis.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CostRecord:
    """Record of a single cost event."""
    layer: int
    cost: float
    category: str
    method: str
    timestamp: str
    confidence: float = 0.0


class CostTracker:
    """
    Tracks and reports costs across all SPL layers.
    
    Provides detailed cost breakdown, suppression rates,
    and cost reduction analysis.
    
    Attributes:
        records: List of all cost records
        layer_costs: Cumulative costs by layer
        layer_counts: Request counts by layer
    """
    
    def __init__(self):
        """Initialize cost tracker."""
        self.records: List[CostRecord] = []
        self.layer_costs: Dict[int, float] = {0: 0.0, 1: 0.0, 2: 0.0}
        self.layer_counts: Dict[int, int] = {0: 0, 1: 0, 2: 0}
        self._suppressions = 0
        self._baseline_cost_per_request = 0.01  # Cost if everything went to Layer 2
        
    def record(self, result: Dict[str, Any]) -> None:
        """
        Record a decision result.
        
        Args:
            result: Dictionary with 'layer', 'cost', 'category', 'method', 'confidence'
        """
        layer = result.get('layer', 2)
        cost = result.get('cost', 0.0)
        category = result.get('category', 'unknown')
        method = result.get('method', 'unknown')
        confidence = result.get('confidence', 0.0)
        
        record = CostRecord(
            layer=layer,
            cost=cost,
            category=category,
            method=method,
            timestamp=datetime.now().isoformat(),
            confidence=confidence,
        )
        
        self.records.append(record)
        self.layer_costs[layer] = self.layer_costs.get(layer, 0.0) + cost
        self.layer_counts[layer] = self.layer_counts.get(layer, 0) + 1
        
        # Track suppressions (requests that avoided Layer 2)
        if layer < 2:
            self._suppressions += 1
    
    def record_result(self, result: Any) -> None:
        """
        Record a result object (Decision or similar).
        
        Args:
            result: Object with layer, cost, category, method, confidence attributes
        """
        self.record({
            'layer': getattr(result, 'layer', 2),
            'cost': getattr(result, 'cost', 0.0),
            'category': getattr(result, 'category', 'unknown'),
            'method': getattr(result, 'method', 'unknown'),
            'confidence': getattr(result, 'confidence', 0.0),
        })
    
    @property
    def total_requests(self) -> int:
        """Total number of requests processed."""
        return sum(self.layer_counts.values())
    
    @property
    def total_cost(self) -> float:
        """Total cost across all layers."""
        return sum(self.layer_costs.values())
    
    @property
    def baseline_cost(self) -> float:
        """Baseline cost if all requests went to Layer 2."""
        return self.total_requests * self._baseline_cost_per_request
    
    @property
    def cost_savings(self) -> float:
        """Total cost savings from using SPL."""
        return self.baseline_cost - self.total_cost
    
    @property
    def suppression_rate(self) -> float:
        """Rate of requests that avoided Layer 2."""
        if self.total_requests == 0:
            return 0.0
        return self._suppressions / self.total_requests
    
    @property
    def cost_reduction_factor(self) -> float:
        """Factor by which costs are reduced."""
        if self.total_cost == 0:
            return float('inf') if self.baseline_cost > 0 else 1.0
        return self.baseline_cost / self.total_cost
    
    def set_baseline_cost(self, cost: float) -> None:
        """Set the baseline cost per request."""
        self._baseline_cost_per_request = cost
    
    def report(self) -> Dict[str, Any]:
        """
        Generate comprehensive cost report.
        
        Returns:
            Dictionary with cost analysis and metrics
        """
        return {
            'total_requests': self.total_requests,
            'total_cost': self.total_cost,
            'baseline_cost': self.baseline_cost,
            'cost_savings': self.cost_savings,
            'cost_reduction_factor': self.cost_reduction_factor,
            'suppression_rate': self.suppression_rate,
            'suppressions': self._suppressions,
            'layer_breakdown': {
                'layer_0': {
                    'count': self.layer_counts.get(0, 0),
                    'cost': self.layer_costs.get(0, 0.0),
                    'percentage': self._layer_percentage(0),
                },
                'layer_1': {
                    'count': self.layer_counts.get(1, 0),
                    'cost': self.layer_costs.get(1, 0.0),
                    'percentage': self._layer_percentage(1),
                },
                'layer_2': {
                    'count': self.layer_counts.get(2, 0),
                    'cost': self.layer_costs.get(2, 0.0),
                    'percentage': self._layer_percentage(2),
                },
            },
        }
    
    def _layer_percentage(self, layer: int) -> float:
        """Calculate percentage of requests handled by a layer."""
        if self.total_requests == 0:
            return 0.0
        return (self.layer_counts.get(layer, 0) / self.total_requests) * 100
    
    def summary(self) -> str:
        """Generate human-readable summary."""
        report = self.report()
        return (
            f"SPL Cost Report\n"
            f"===============\n"
            f"Total requests: {report['total_requests']}\n"
            f"Total cost: ${report['total_cost']:.4f}\n"
            f"Baseline cost: ${report['baseline_cost']:.4f}\n"
            f"Savings: ${report['cost_savings']:.4f}\n"
            f"Cost reduction: {report['cost_reduction_factor']:.1f}x\n"
            f"Suppression rate: {report['suppression_rate']:.1%}\n"
            f"\n"
            f"Layer breakdown:\n"
            f"  Layer 0: {report['layer_breakdown']['layer_0']['count']} requests "
            f"({report['layer_breakdown']['layer_0']['percentage']:.1f}%)\n"
            f"  Layer 1: {report['layer_breakdown']['layer_1']['count']} requests "
            f"({report['layer_breakdown']['layer_1']['percentage']:.1f}%)\n"
            f"  Layer 2: {report['layer_breakdown']['layer_2']['count']} requests "
            f"({report['layer_breakdown']['layer_2']['percentage']:.1f}%)\n"
        )
    
    def reset(self) -> None:
        """Reset all tracking data."""
        self.records.clear()
        self.layer_costs = {0: 0.0, 1: 0.0, 2: 0.0}
        self.layer_counts = {0: 0, 1: 0, 2: 0}
        self._suppressions = 0
    
    def get_records_by_layer(self, layer: int) -> List[CostRecord]:
        """Get all records for a specific layer."""
        return [r for r in self.records if r.layer == layer]
    
    def get_records_by_category(self, category: str) -> List[CostRecord]:
        """Get all records for a specific category."""
        return [r for r in self.records if r.category == category]
