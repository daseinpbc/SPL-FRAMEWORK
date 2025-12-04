"""
Test Layer 2: Deliberative (Foundation Model Reasoning)

Tests for the Layer2Deliberative class which handles:
- Foundation model integration
- Complex reasoning
- Pattern learning triggers
"""

import pytest
from spl.layer2_deliberative import Layer2Deliberative, DeliberativeResult


class TestLayer2Deliberative:
    """Tests for Layer 2 deliberative reasoning."""

    def test_initialization_default(self):
        """Test default initialization."""
        layer2 = Layer2Deliberative()
        assert layer2.model_client is None
        assert layer2.cost_per_call == 0.01
        assert layer2.model_name == "simulated"
        assert layer2.call_count == 0
        assert layer2.total_cost == 0.0

    def test_initialization_with_params(self):
        """Test initialization with custom parameters."""
        layer2 = Layer2Deliberative(
            cost_per_call=0.02,
            model_name="custom_model"
        )
        assert layer2.cost_per_call == 0.02
        assert layer2.model_name == "custom_model"

    def test_simulated_reason_urgent(self):
        """Test simulated reasoning for urgent content."""
        layer2 = Layer2Deliberative()
        result = layer2.reason("This is an urgent request!")
        assert isinstance(result, DeliberativeResult)
        assert result.category == 'urgent'
        assert result.confidence > 0.90
        assert result.cost == 0.01

    def test_simulated_reason_billing(self):
        """Test simulated reasoning for billing content."""
        layer2 = Layer2Deliberative()
        result = layer2.reason("Please send me the invoice for the payment.")
        assert result.category == 'billing'
        assert result.confidence > 0.80

    def test_simulated_reason_spam(self):
        """Test simulated reasoning for spam content."""
        layer2 = Layer2Deliberative()
        result = layer2.reason("Click here to unsubscribe from this list.")
        assert result.category == 'spam'
        assert result.confidence > 0.90

    def test_simulated_reason_other(self):
        """Test simulated reasoning for uncategorized content."""
        layer2 = Layer2Deliberative()
        result = layer2.reason("Just a random message about nothing special.")
        assert result.category == 'other'
        assert result.confidence > 0.0

    def test_call_count_increment(self):
        """Test that call count increments."""
        layer2 = Layer2Deliberative()
        assert layer2.call_count == 0
        layer2.reason("Message 1")
        assert layer2.call_count == 1
        layer2.reason("Message 2")
        assert layer2.call_count == 2

    def test_total_cost_accumulation(self):
        """Test that total cost accumulates."""
        layer2 = Layer2Deliberative(cost_per_call=0.01)
        assert layer2.total_cost == 0.0
        layer2.reason("Message 1")
        assert layer2.total_cost == 0.01
        layer2.reason("Message 2")
        assert layer2.total_cost == 0.02

    def test_reset_tracking(self):
        """Test resetting call count and cost tracking."""
        layer2 = Layer2Deliberative()
        layer2.reason("Message 1")
        layer2.reason("Message 2")
        assert layer2.call_count > 0
        assert layer2.total_cost > 0.0
        layer2.reset_tracking()
        assert layer2.call_count == 0
        assert layer2.total_cost == 0.0

    def test_set_model_client(self):
        """Test setting a model client."""
        layer2 = Layer2Deliberative()
        mock_client = object()
        layer2.set_model_client(mock_client)
        assert layer2.model_client is mock_client

    def test_set_cost_per_call(self):
        """Test setting cost per call."""
        layer2 = Layer2Deliberative()
        assert layer2.cost_per_call == 0.01
        layer2.set_cost_per_call(0.05)
        assert layer2.cost_per_call == 0.05

    def test_report_generation(self):
        """Test report generation."""
        layer2 = Layer2Deliberative(cost_per_call=0.01, model_name="test_model")
        layer2.reason("Test message")
        report = layer2.report()
        assert report['layer'] == 2
        assert report['name'] == 'deliberative'
        assert report['model'] == 'test_model'
        assert report['calls'] == 1
        assert report['cost_per_call'] == 0.01
        assert report['total_cost'] == 0.01
        assert report['has_model_client'] is False

    def test_report_with_model_client(self):
        """Test report generation with model client."""
        layer2 = Layer2Deliberative()
        layer2.set_model_client(object())
        report = layer2.report()
        assert report['has_model_client'] is True

    def test_result_includes_reasoning(self):
        """Test that result includes reasoning explanation."""
        layer2 = Layer2Deliberative()
        result = layer2.reason("This is urgent!")
        assert result.reasoning is not None
        assert len(result.reasoning) > 0

    def test_result_includes_model_name(self):
        """Test that result includes model name."""
        layer2 = Layer2Deliberative(model_name="custom_model")
        result = layer2.reason("Test message")
        assert result.model == "custom_model"

    def test_case_insensitive_categorization(self):
        """Test that categorization is case-insensitive."""
        layer2 = Layer2Deliberative()
        result1 = layer2.reason("URGENT message")
        result2 = layer2.reason("urgent message")
        assert result1.category == result2.category

    def test_asap_triggers_urgent(self):
        """Test that ASAP triggers urgent category."""
        layer2 = Layer2Deliberative()
        result = layer2.reason("Need this done ASAP please")
        assert result.category == 'urgent'

    def test_emergency_triggers_urgent(self):
        """Test that emergency triggers urgent category."""
        layer2 = Layer2Deliberative()
        result = layer2.reason("This is an emergency situation!")
        assert result.category == 'urgent'

    def test_payment_triggers_billing(self):
        """Test that payment triggers billing category."""
        layer2 = Layer2Deliberative()
        result = layer2.reason("Payment confirmation needed")
        assert result.category == 'billing'

    def test_lottery_triggers_spam(self):
        """Test that lottery triggers spam category."""
        layer2 = Layer2Deliberative()
        result = layer2.reason("You won the lottery!")
        assert result.category == 'spam'

    def test_viagra_triggers_spam(self):
        """Test that viagra triggers spam category."""
        layer2 = Layer2Deliberative()
        result = layer2.reason("Buy discount viagra now")
        assert result.category == 'spam'
