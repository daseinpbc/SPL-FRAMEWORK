"""
Test Cost Tracker - Cost Monitoring & Reporting

Tests for the CostTracker class which handles:
- Recording costs
- Tracking suppressions
- Generating reports
"""

import pytest
from spl.cost_tracker import CostTracker, CostRecord


class TestCostTracker:
    """Tests for the CostTracker."""

    def test_initialization(self):
        """Test default initialization."""
        tracker = CostTracker()
        assert tracker.total_requests == 0
        assert tracker.total_cost == 0.0
        assert len(tracker.records) == 0

    def test_record_dict(self):
        """Test recording a result dictionary."""
        tracker = CostTracker()
        tracker.record({
            'layer': 1,
            'cost': 0.001,
            'category': 'urgent',
            'method': 'pattern',
            'confidence': 0.95
        })
        assert tracker.total_requests == 1
        assert tracker.total_cost == 0.001
        assert len(tracker.records) == 1

    def test_record_result_object(self):
        """Test recording a result object with attributes."""
        tracker = CostTracker()

        class MockResult:
            layer = 2
            cost = 0.01
            category = 'other'
            method = 'llm'
            confidence = 0.75

        tracker.record_result(MockResult())
        assert tracker.total_requests == 1
        assert tracker.total_cost == 0.01

    def test_layer_tracking(self):
        """Test that costs are tracked per layer."""
        tracker = CostTracker()
        tracker.record({'layer': 0, 'cost': 0.0, 'category': 'test', 'method': 'validation'})
        tracker.record({'layer': 1, 'cost': 0.001, 'category': 'test', 'method': 'pattern'})
        tracker.record({'layer': 2, 'cost': 0.01, 'category': 'test', 'method': 'llm'})
        assert tracker.layer_counts[0] == 1
        assert tracker.layer_counts[1] == 1
        assert tracker.layer_counts[2] == 1
        assert tracker.layer_costs[0] == 0.0
        assert tracker.layer_costs[1] == 0.001
        assert tracker.layer_costs[2] == 0.01

    def test_suppression_tracking(self):
        """Test suppression tracking for Layer 0 and 1."""
        tracker = CostTracker()
        # Layer 0 suppresses
        tracker.record({'layer': 0, 'cost': 0.0, 'category': 'test', 'method': 'validation'})
        # Layer 1 suppresses
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'test', 'method': 'pattern'})
        # Layer 2 does not suppress
        tracker.record({'layer': 2, 'cost': 0.01, 'category': 'test', 'method': 'llm'})
        assert tracker._suppressions == 2

    def test_suppression_rate(self):
        """Test suppression rate calculation."""
        tracker = CostTracker()
        # 2 suppressions out of 4 requests
        tracker.record({'layer': 0, 'cost': 0.0, 'category': 'test', 'method': 'validation'})
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'test', 'method': 'pattern'})
        tracker.record({'layer': 2, 'cost': 0.01, 'category': 'test', 'method': 'llm'})
        tracker.record({'layer': 2, 'cost': 0.01, 'category': 'test', 'method': 'llm'})
        assert tracker.suppression_rate == 0.5

    def test_suppression_rate_zero_requests(self):
        """Test suppression rate with zero requests."""
        tracker = CostTracker()
        assert tracker.suppression_rate == 0.0

    def test_baseline_cost(self):
        """Test baseline cost calculation."""
        tracker = CostTracker()
        tracker.record({'layer': 0, 'cost': 0.0, 'category': 'test', 'method': 'validation'})
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'test', 'method': 'pattern'})
        assert tracker.baseline_cost == 0.02  # 2 requests * $0.01

    def test_cost_savings(self):
        """Test cost savings calculation."""
        tracker = CostTracker()
        # Both handled by Layer 0/1 with 0 cost
        tracker.record({'layer': 0, 'cost': 0.0, 'category': 'test', 'method': 'validation'})
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'test', 'method': 'pattern'})
        # Baseline: 2 * $0.01 = $0.02, Actual: $0.00
        assert tracker.cost_savings == 0.02

    def test_cost_reduction_factor(self):
        """Test cost reduction factor calculation."""
        tracker = CostTracker()
        tracker.record({'layer': 2, 'cost': 0.01, 'category': 'test', 'method': 'llm'})
        # Baseline: $0.01, Actual: $0.01, Reduction: 1.0x
        assert tracker.cost_reduction_factor == 1.0

    def test_cost_reduction_factor_with_savings(self):
        """Test cost reduction factor with savings."""
        tracker = CostTracker()
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'test', 'method': 'pattern'})
        tracker.record({'layer': 2, 'cost': 0.01, 'category': 'test', 'method': 'llm'})
        # Baseline: $0.02, Actual: $0.01, Reduction: 2.0x
        assert tracker.cost_reduction_factor == 2.0

    def test_cost_reduction_factor_zero_cost(self):
        """Test cost reduction factor when actual cost is zero."""
        tracker = CostTracker()
        tracker.record({'layer': 0, 'cost': 0.0, 'category': 'test', 'method': 'validation'})
        # Baseline: $0.01, Actual: $0.00, Reduction: inf
        assert tracker.cost_reduction_factor == float('inf')

    def test_set_baseline_cost(self):
        """Test setting baseline cost per request."""
        tracker = CostTracker()
        tracker.set_baseline_cost(0.05)
        tracker.record({'layer': 0, 'cost': 0.0, 'category': 'test', 'method': 'validation'})
        assert tracker.baseline_cost == 0.05

    def test_report_generation(self):
        """Test comprehensive report generation."""
        tracker = CostTracker()
        tracker.record({'layer': 0, 'cost': 0.0, 'category': 'rejected', 'method': 'validation'})
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'urgent', 'method': 'pattern'})
        tracker.record({'layer': 2, 'cost': 0.01, 'category': 'other', 'method': 'llm'})
        report = tracker.report()
        assert report['total_requests'] == 3
        assert report['total_cost'] == pytest.approx(0.01)
        assert report['baseline_cost'] == pytest.approx(0.03)
        assert report['cost_savings'] == pytest.approx(0.02)
        assert 'cost_reduction_factor' in report
        assert 'suppression_rate' in report
        assert 'layer_breakdown' in report
        assert 'layer_0' in report['layer_breakdown']
        assert 'layer_1' in report['layer_breakdown']
        assert 'layer_2' in report['layer_breakdown']

    def test_summary_generation(self):
        """Test human-readable summary generation."""
        tracker = CostTracker()
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'urgent', 'method': 'pattern'})
        summary = tracker.summary()
        assert 'SPL Cost Report' in summary
        assert 'Total requests:' in summary
        assert 'Total cost:' in summary
        assert 'Layer breakdown:' in summary

    def test_reset(self):
        """Test resetting tracker state."""
        tracker = CostTracker()
        tracker.record({'layer': 1, 'cost': 0.001, 'category': 'test', 'method': 'pattern'})
        tracker.reset()
        assert tracker.total_requests == 0
        assert tracker.total_cost == 0.0
        assert len(tracker.records) == 0
        assert tracker._suppressions == 0

    def test_get_records_by_layer(self):
        """Test filtering records by layer."""
        tracker = CostTracker()
        tracker.record({'layer': 0, 'cost': 0.0, 'category': 'test', 'method': 'validation'})
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'test', 'method': 'pattern'})
        tracker.record({'layer': 2, 'cost': 0.01, 'category': 'test', 'method': 'llm'})
        layer1_records = tracker.get_records_by_layer(1)
        assert len(layer1_records) == 1
        assert layer1_records[0].layer == 1

    def test_get_records_by_category(self):
        """Test filtering records by category."""
        tracker = CostTracker()
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'urgent', 'method': 'pattern'})
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'billing', 'method': 'pattern'})
        tracker.record({'layer': 2, 'cost': 0.01, 'category': 'urgent', 'method': 'llm'})
        urgent_records = tracker.get_records_by_category('urgent')
        assert len(urgent_records) == 2
        for record in urgent_records:
            assert record.category == 'urgent'

    def test_cost_record_dataclass(self):
        """Test CostRecord dataclass."""
        record = CostRecord(
            layer=1,
            cost=0.001,
            category='urgent',
            method='pattern',
            timestamp='2025-01-01T00:00:00',
            confidence=0.95
        )
        assert record.layer == 1
        assert record.cost == 0.001
        assert record.category == 'urgent'
        assert record.method == 'pattern'
        assert record.confidence == 0.95

    def test_layer_percentage_calculation(self):
        """Test layer percentage calculation."""
        tracker = CostTracker()
        tracker.record({'layer': 0, 'cost': 0.0, 'category': 'test', 'method': 'validation'})
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'test', 'method': 'pattern'})
        tracker.record({'layer': 1, 'cost': 0.0, 'category': 'test', 'method': 'pattern'})
        tracker.record({'layer': 2, 'cost': 0.01, 'category': 'test', 'method': 'llm'})
        # 1/4 = 25%, 2/4 = 50%, 1/4 = 25%
        report = tracker.report()
        assert report['layer_breakdown']['layer_0']['percentage'] == 25.0
        assert report['layer_breakdown']['layer_1']['percentage'] == 50.0
        assert report['layer_breakdown']['layer_2']['percentage'] == 25.0
