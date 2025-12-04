"""
Test Layer 0: Reactive Schemas (Validation)

Tests for the Layer0Reactive class which handles:
- Format validation
- Permission checks
- Rate limiting
- Blocklist/allowlist matching
"""

import pytest
from spl.layer0_reactive import Layer0Reactive, ValidationResult


class TestLayer0Reactive:
    """Tests for Layer 0 reactive validation."""

    def test_valid_request(self):
        """Test that a valid request passes validation."""
        layer0 = Layer0Reactive()
        request = {'user_id': 'user123', 'content': 'This is a valid request content.'}
        result = layer0.validate(request)
        assert result.valid is True
        assert result.rejected is False

    def test_content_too_short(self):
        """Test rejection when content is too short."""
        layer0 = Layer0Reactive(min_length=10)
        request = {'user_id': 'user123', 'content': 'Short'}
        result = layer0.validate(request)
        assert result.valid is False
        assert result.rejected is True
        assert 'too short' in result.reason

    def test_content_too_long(self):
        """Test rejection when content is too long."""
        layer0 = Layer0Reactive(max_length=50)
        request = {'user_id': 'user123', 'content': 'A' * 100}
        result = layer0.validate(request)
        assert result.valid is False
        assert result.rejected is True
        assert 'too long' in result.reason

    def test_content_not_string(self):
        """Test rejection when content is not a string."""
        layer0 = Layer0Reactive()
        request = {'user_id': 'user123', 'content': 12345}
        result = layer0.validate(request)
        assert result.valid is False
        assert result.rejected is True
        assert 'string' in result.reason

    def test_blocklist_detection(self):
        """Test that blocked terms are detected."""
        layer0 = Layer0Reactive(blocklist={'spam', 'blocked'})
        request = {'user_id': 'user123', 'content': 'This message contains spam content.'}
        result = layer0.validate(request)
        assert result.valid is False
        assert result.rejected is True
        assert 'Blocked term' in result.reason

    def test_blocklist_case_insensitive(self):
        """Test that blocklist matching is case-insensitive."""
        layer0 = Layer0Reactive(blocklist={'spam'})
        request = {'user_id': 'user123', 'content': 'This message contains SPAM content.'}
        result = layer0.validate(request)
        assert result.valid is False

    def test_add_to_blocklist(self):
        """Test adding terms to blocklist."""
        layer0 = Layer0Reactive()
        layer0.add_to_blocklist('forbidden')
        request = {'user_id': 'user123', 'content': 'This contains a forbidden word.'}
        result = layer0.validate(request)
        assert result.valid is False

    def test_remove_from_blocklist(self):
        """Test removing terms from blocklist."""
        layer0 = Layer0Reactive(blocklist={'spam'})
        layer0.remove_from_blocklist('spam')
        request = {'user_id': 'user123', 'content': 'This message contains spam content.'}
        result = layer0.validate(request)
        assert result.valid is True

    def test_add_to_allowlist(self):
        """Test adding terms to allowlist."""
        layer0 = Layer0Reactive()
        layer0.add_to_allowlist('trusted')
        assert 'trusted' in layer0.allowlist

    def test_validation_count_increment(self):
        """Test that validation count increments correctly."""
        layer0 = Layer0Reactive()
        assert layer0.validation_count == 0
        request = {'user_id': 'user123', 'content': 'Valid content here'}
        layer0.validate(request)
        assert layer0.validation_count == 1
        layer0.validate(request)
        assert layer0.validation_count == 2

    def test_reset_rate_limits(self):
        """Test resetting rate limits."""
        layer0 = Layer0Reactive()
        request = {'user_id': 'user123', 'content': 'Valid content here'}
        layer0.validate(request)
        assert len(layer0.rate_limits) > 0
        layer0.reset_rate_limits()
        assert len(layer0.rate_limits) == 0

    def test_report_generation(self):
        """Test report generation."""
        layer0 = Layer0Reactive(blocklist={'spam', 'blocked'})
        request = {'user_id': 'user123', 'content': 'Valid content here'}
        layer0.validate(request)
        report = layer0.report()
        assert report['layer'] == 0
        assert report['name'] == 'reactive'
        assert report['validations'] == 1
        assert report['blocklist_size'] == 2
        assert report['cost'] == 0.0

    def test_default_user_id(self):
        """Test that requests without user_id still work."""
        layer0 = Layer0Reactive()
        request = {'content': 'Valid content without user_id'}
        result = layer0.validate(request)
        assert result.valid is True

    def test_empty_content(self):
        """Test rejection of empty content."""
        layer0 = Layer0Reactive()
        request = {'user_id': 'user123', 'content': ''}
        result = layer0.validate(request)
        assert result.valid is False
        assert result.rejected is True
