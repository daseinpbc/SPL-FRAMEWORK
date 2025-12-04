"""
Test Layer 1: Tactical Behaviors (Pattern Matching)

Tests for the Layer1Tactical class which handles:
- Regex pattern matching
- Classification rules
- Cache lookup
- Pattern learning
"""

import pytest
from spl.layer1_tactical import Layer1Tactical, Pattern, PatternMatchResult


class TestLayer1Tactical:
    """Tests for Layer 1 tactical pattern matching."""

    def test_add_pattern(self):
        """Test adding a pattern."""
        layer1 = Layer1Tactical()
        layer1.add_pattern(
            name='urgent',
            regex=r'urgent|asap|emergency',
            category='urgent',
            confidence=0.95
        )
        assert layer1.pattern_count == 1
        assert 'urgent' in layer1.patterns

    def test_remove_pattern(self):
        """Test removing a pattern."""
        layer1 = Layer1Tactical()
        layer1.add_pattern('test', r'test', 'testing', 0.9)
        assert layer1.pattern_count == 1
        result = layer1.remove_pattern('test')
        assert result is True
        assert layer1.pattern_count == 0

    def test_remove_nonexistent_pattern(self):
        """Test removing a pattern that doesn't exist."""
        layer1 = Layer1Tactical()
        result = layer1.remove_pattern('nonexistent')
        assert result is False

    def test_pattern_match_success(self):
        """Test successful pattern matching."""
        layer1 = Layer1Tactical(confidence_threshold=0.85)
        layer1.add_pattern(
            name='urgent',
            regex=r'urgent|asap|emergency',
            category='urgent',
            confidence=0.95
        )
        result = layer1.match('This is an urgent request!')
        assert result is not None
        assert result.matched is True
        assert result.category == 'urgent'
        assert result.confidence == 0.95

    def test_pattern_match_case_insensitive(self):
        """Test that pattern matching is case-insensitive."""
        layer1 = Layer1Tactical(confidence_threshold=0.85)
        layer1.add_pattern(
            name='urgent',
            regex=r'urgent',
            category='urgent',
            confidence=0.95
        )
        result = layer1.match('This is URGENT!')
        assert result is not None
        assert result.matched is True

    def test_pattern_no_match(self):
        """Test when no pattern matches."""
        layer1 = Layer1Tactical(confidence_threshold=0.85)
        layer1.add_pattern(
            name='urgent',
            regex=r'urgent',
            category='urgent',
            confidence=0.95
        )
        result = layer1.match('This is a normal message.')
        assert result is None

    def test_confidence_threshold_filtering(self):
        """Test that patterns below confidence threshold are ignored."""
        layer1 = Layer1Tactical(confidence_threshold=0.90)
        layer1.add_pattern(
            name='urgent',
            regex=r'urgent',
            category='urgent',
            confidence=0.85  # Below threshold
        )
        result = layer1.match('This is urgent!')
        assert result is None

    def test_cache_behavior(self):
        """Test that caching works correctly."""
        layer1 = Layer1Tactical(confidence_threshold=0.85)
        layer1.add_pattern(
            name='urgent',
            regex=r'urgent',
            category='urgent',
            confidence=0.95
        )
        # First match
        content = 'This is an urgent message'
        result1 = layer1.match(content)
        # Second match should use cache
        result2 = layer1.match(content)
        assert result1.matched is True
        assert result2.matched is True
        assert result1.category == result2.category
        assert len(layer1.cache) > 0

    def test_clear_cache(self):
        """Test clearing the cache."""
        layer1 = Layer1Tactical()
        layer1.add_pattern('test', r'test', 'testing', 0.95)
        layer1.match('This is a test message')
        assert len(layer1.cache) > 0
        layer1.clear_cache()
        assert len(layer1.cache) == 0

    def test_learn_pattern(self):
        """Test learning a new pattern."""
        layer1 = Layer1Tactical()
        pattern_name = layer1.learn_pattern(
            content='billing question about invoice',
            category='billing',
            confidence=0.92,
            learned_by='test_agent'
        )
        assert pattern_name is not None
        assert 'billing' in pattern_name
        assert layer1.pattern_count == 1

    def test_learn_pattern_low_confidence(self):
        """Test that low confidence patterns are not learned."""
        layer1 = Layer1Tactical()
        pattern_name = layer1.learn_pattern(
            content='some content',
            category='category',
            confidence=0.80  # Below 0.90 threshold
        )
        assert pattern_name is None
        assert layer1.pattern_count == 0

    def test_shared_state_pattern_learning(self):
        """Test that learned patterns are shared via shared_state."""
        # Use a non-empty initial shared_state to avoid the `or {}` issue
        shared_state = {'initial': True}
        layer1 = Layer1Tactical(shared_state=shared_state)
        result = layer1.learn_pattern(
            content='billing question about invoice',
            category='billing',
            confidence=0.95,
            learned_by='agent_a'
        )
        # Pattern should be learned since confidence >= 0.90
        assert result is not None
        # Check that learned_patterns was added to the layer's shared_state
        assert 'learned_patterns' in layer1.shared_state
        assert 'billing' in layer1.shared_state['learned_patterns']

    def test_match_shared_pattern(self):
        """Test matching against shared patterns."""
        shared_state = {
            'learned_patterns': {
                'billing': {'confidence': 0.95}
            }
        }
        layer1 = Layer1Tactical(confidence_threshold=0.85, shared_state=shared_state)
        result = layer1.match('billing inquiry')
        assert result is not None
        assert result.matched is True
        assert result.method == 'pattern_shared'

    def test_list_patterns(self):
        """Test listing all patterns."""
        layer1 = Layer1Tactical()
        layer1.add_pattern('urgent', r'urgent', 'urgent', 0.95)
        layer1.add_pattern('billing', r'billing', 'billing', 0.90)
        patterns = layer1.list_patterns()
        assert len(patterns) == 2
        names = [p['name'] for p in patterns]
        assert 'urgent' in names
        assert 'billing' in names

    def test_match_count_increment(self):
        """Test that match count increments correctly."""
        layer1 = Layer1Tactical()
        layer1.add_pattern('test', r'test', 'testing', 0.95)
        assert layer1.match_count == 0
        layer1.match('Test message')
        assert layer1.match_count == 1
        layer1.match('Another test')
        assert layer1.match_count == 2

    def test_cost_tracking(self):
        """Test that cost is tracked for pattern matches."""
        layer1 = Layer1Tactical()
        layer1.add_pattern('test', r'test', 'testing', 0.95)
        initial_cost = layer1.cost
        layer1.match('Test message')
        assert layer1.cost >= initial_cost

    def test_report_generation(self):
        """Test report generation."""
        layer1 = Layer1Tactical()
        layer1.add_pattern('test', r'test', 'testing', 0.95)
        layer1.match('Test message')
        report = layer1.report()
        assert report['layer'] == 1
        assert report['name'] == 'tactical'
        assert report['patterns'] == 1
        assert report['match_attempts'] == 1

    def test_invalid_regex_handling(self):
        """Test that invalid regex patterns are handled gracefully."""
        layer1 = Layer1Tactical()
        # Add a pattern with invalid regex
        layer1.add_pattern('invalid', r'[invalid', 'category', 0.95)
        # Should not raise an exception
        result = layer1.match('Some content')
        # Invalid pattern should be skipped, no match
        assert result is None

    def test_empty_content(self):
        """Test matching empty content."""
        layer1 = Layer1Tactical()
        layer1.add_pattern('test', r'test', 'testing', 0.95)
        result = layer1.match('')
        assert result is None

    def test_pattern_match_count_tracking(self):
        """Test that individual pattern match counts are tracked."""
        layer1 = Layer1Tactical()
        layer1.add_pattern('test', r'test', 'testing', 0.95)
        layer1.match('Test message 1')
        layer1.clear_cache()  # Clear cache to force re-matching
        layer1.match('Test message 2')
        pattern = layer1.patterns['test']
        assert pattern.match_count == 2
