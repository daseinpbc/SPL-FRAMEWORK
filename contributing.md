# Contributing to SPL

We welcome contributions to Subsumption Pattern Learning! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Issues
- Use GitHub Issues for bug reports and feature requests
- Include clear description, steps to reproduce, and expected behavior
- Add relevant labels (bug, enhancement, documentation, etc.)

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Write or update tests
5. Update documentation if needed
6. Submit PR with clear description

### Code Style
- Follow PEP 8 guidelines
- Use type hints for functions
- Add docstrings to classes and functions
- Keep functions focused and testable

### Testing
- Write unit tests for new features
- Run `pytest tests/` before submitting
- Aim for >80% code coverage
- Test with multiple Python versions (3.8+)

### Documentation
- Update README.md for user-facing changes
- Add docstrings following Google style
- Update ARCHITECTURE.md for architecture changes
- Add examples for new features

## Development Setup

```bash
# Clone and install
git clone https://github.com/daseinpbc/SPL-FRAMEWORK.git
cd SPL-FRAMEWORK
pip install -e ".[dev]"

# Run tests
pytest tests/

# Code quality checks
black spl/
flake8 spl/
mypy spl/
```

## Release Process
1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create git tag
4. Push to PyPI

## Questions?
- Open a discussion on GitHub
- Email: PAMELA@dasein.works

Thank you for contributing!
