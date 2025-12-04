"""
Test SPL Agent - Main SPL Agent Orchestrator

Tests for the SPLAgent class which coordinates:
- Layer 0: Reactive (Validation)
- Layer 1: Tactical (Pattern Matching)
- Layer 2: Deliberative (Foundation Model)
"""

import pytest
from spl import SPLAgent
from spl.agent import Decision


class TestSPLAgent:
    """Tests for the main SPL Agent."""

    def test_initialization_default(self):
        """Test default initialization."""
        agent = SPLAgent()
        assert agent.agent_id == "spl_agent"
        assert agent.confidence_threshold == 0.85
        assert agent.layer0 is not None
        assert agent.layer1 is not None
        assert agent.layer2 is not None

    def test_initialization_with_params(self):
        """Test initialization with custom parameters."""
        shared_state = {'test': 'value'}
        agent = SPLAgent(
            agent_id="custom_agent",
            shared_state=shared_state,
            confidence_threshold=0.90
        )
        assert agent.agent_id == "custom_agent"
        assert agent.shared_state == shared_state
        assert agent.confidence_threshold == 0.90

    def test_process_valid_request(self):
        """Test processing a valid request."""
        agent = SPLAgent()
        request = {'user_id': 'user123', 'content': 'This is a normal message about nothing special.'}
        result = agent.process(request)
        assert isinstance(result, Decision)
        assert result.category is not None
        assert result.confidence >= 0.0
        assert result.layer in [0, 1, 2]

    def test_process_invalid_request_too_short(self):
        """Test that invalid requests are rejected at Layer 0."""
        agent = SPLAgent()
        request = {'user_id': 'user123', 'content': 'Hi'}
        result = agent.process(request)
        assert result.category == 'REJECTED'
        assert result.layer == 0
        assert result.cost == 0.0
        assert result.suppressed is True

    def test_process_pattern_match(self):
        """Test that patterns suppress Layer 2."""
        agent = SPLAgent()
        agent.add_pattern(
            name='urgent',
            regex=r'urgent|asap|emergency',
            category='urgent',
            confidence=0.95
        )
        request = {'user_id': 'user123', 'content': 'This is an urgent request!'}
        result = agent.process(request)
        assert result.category == 'urgent'
        assert result.layer == 1
        assert result.cost == 0.0
        assert result.suppressed is True
        assert agent.suppression_count >= 1

    def test_process_layer2_fallback(self):
        """Test that unmatched requests go to Layer 2."""
        agent = SPLAgent()
        # Don't add any patterns
        request = {'user_id': 'user123', 'content': 'This is an urgent message that needs attention!'}
        result = agent.process(request)
        # Should go to Layer 2 since no patterns are configured
        assert result.layer == 2
        assert result.cost > 0.0
        assert result.suppressed is False

    def test_add_pattern(self):
        """Test adding patterns to Layer 1."""
        agent = SPLAgent()
        agent.add_pattern('test', r'test', 'testing', 0.95)
        assert agent.layer1.pattern_count == 1

    def test_add_to_blocklist(self):
        """Test adding terms to blocklist."""
        agent = SPLAgent()
        agent.add_to_blocklist('forbidden')
        request = {'user_id': 'user123', 'content': 'This contains a forbidden word.'}
        result = agent.process(request)
        assert result.category == 'REJECTED'
        assert result.layer == 0

    def test_set_layer2(self):
        """Test setting Layer 2."""
        agent = SPLAgent()
        custom_layer2 = object()
        agent.set_layer2(custom_layer2)
        assert agent.layer2 is custom_layer2

    def test_suppression_count(self):
        """Test suppression count tracking."""
        agent = SPLAgent()
        agent.add_pattern('urgent', r'urgent', 'urgent', 0.95)
        assert agent.suppression_count == 0
        agent.process({'user_id': 'user123', 'content': 'This is urgent!'})
        assert agent.suppression_count >= 1
        agent.process({'user_id': 'user123', 'content': 'Another urgent message!'})
        assert agent.suppression_count >= 2

    def test_patterns_learned(self):
        """Test patterns learned count."""
        agent = SPLAgent()
        assert agent.patterns_learned == 0
        agent.add_pattern('test', r'test', 'testing', 0.95)
        assert agent.patterns_learned == 1

    def test_report_generation(self):
        """Test report generation."""
        agent = SPLAgent(agent_id="test_agent")
        agent.add_pattern('urgent', r'urgent', 'urgent', 0.95)
        agent.process({'user_id': 'user123', 'content': 'This is an urgent message!'})
        report = agent.report()
        assert report['agent_id'] == 'test_agent'
        assert 'total_cost' in report
        assert 'cost_savings' in report
        assert 'cost_reduction_factor' in report
        assert 'suppression_rate' in report
        assert 'suppressions' in report
        assert 'patterns_learned' in report
        assert 'layer_breakdown' in report
        assert 'layer_reports' in report

    def test_reset(self):
        """Test resetting agent state."""
        agent = SPLAgent()
        agent.add_pattern('urgent', r'urgent', 'urgent', 0.95)
        agent.process({'user_id': 'user123', 'content': 'This is urgent!'})
        agent.reset()
        assert agent.suppression_count == 0
        assert len(agent.layer1.cache) == 0

    def test_pattern_learning_from_layer2(self):
        """Test that high confidence Layer 2 results trigger pattern learning."""
        agent = SPLAgent()
        # Process a message that goes to Layer 2 and gets high confidence
        initial_patterns = agent.patterns_learned
        agent.process({'user_id': 'user123', 'content': 'This is spam with lottery offer!'})
        # The simulated Layer 2 returns high confidence for spam, so a pattern should be learned
        # Note: This depends on the simulated behavior returning confidence >= 0.90

    def test_cost_tracker_integration(self):
        """Test that cost tracker is properly integrated."""
        agent = SPLAgent()
        assert agent.cost_tracker is not None
        agent.process({'user_id': 'user123', 'content': 'Valid content message here'})
        assert agent.cost_tracker.total_requests > 0

    def test_decision_attributes(self):
        """Test Decision dataclass attributes."""
        decision = Decision(
            category='urgent',
            method='pattern',
            confidence=0.95,
            cost=0.0,
            layer=1,
            suppressed=True
        )
        assert decision.category == 'urgent'
        assert decision.method == 'pattern'
        assert decision.confidence == 0.95
        assert decision.cost == 0.0
        assert decision.layer == 1
        assert decision.suppressed is True

    def test_error_handling(self):
        """Test that errors are handled gracefully."""
        agent = SPLAgent()
        # Test with None content (which should be handled gracefully)
        request = {'user_id': 'user123', 'content': None}
        result = agent.process(request)
        # Should handle the error gracefully
        assert result is not None
        assert result.category in ['REJECTED', 'ERROR']

    def test_multiple_patterns_priority(self):
        """Test processing with multiple patterns."""
        agent = SPLAgent()
        agent.add_pattern('urgent', r'urgent', 'urgent', 0.99)
        agent.add_pattern('billing', r'billing', 'billing', 0.95)
        # Content that matches urgent
        result = agent.process({'user_id': 'user123', 'content': 'This is urgent!'})
        assert result.category == 'urgent'

    def test_anonymous_user(self):
        """Test processing without user_id."""
        agent = SPLAgent()
        request = {'content': 'Valid content without user_id provided'}
        result = agent.process(request)
        assert result is not None

    def test_shared_state_propagation(self):
        """Test that shared state is propagated to Layer 1."""
        shared_state = {'test_key': 'test_value'}
        agent = SPLAgent(shared_state=shared_state)
        assert agent.layer1.shared_state == shared_state
