Contributing to SPL

Thank you for your interest in contributing to Subsumption Pattern Learning (SPL)!

## Development Setup

### 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/spl-framework.git
cd spl-framework
### 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
### 3. Install dependencies
pip install -r requirements.txt
pip install -e .  # Install in editable mode
### 4. Run tests
pytest tests/
## Code Style

We follow Python best practices:

- **Formatting:** Black (line length 100)
- **Linting:** Flake8
- **Type hints:** MyPy

Run before committing:
black .
flake8 .
mypy src/
## Testing

- All new features must include tests
- Maintain >80% code coverage
- Tests should be fast (<1s per test)
Run all testspytestRun with coveragepytest --cov=spl_framework tests/
## Commit Messages

Follow conventional commits:
feat: Add new pattern learning algorithm
fix: Correct Layer 1 confidence calculation
docs: Update integration guide
test: Add tests for multi-agent coordination
## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Run tests and linting
6. Commit your changes
7. Push to your fork
8. Open a Pull Request

## Areas for Contribution

We welcome contributions in:

- **Pattern extraction algorithms:** Better learning from LLM decisions
- **Performance optimizations:** Faster pattern matching
- **LLM integrations:** Support for more providers
- **Multi-agent coordination:** Advanced state sharing
- **Documentation:** Examples, tutorials, guides
- **Benchmarks:** New domains and use cases

## Questions?

Open an issue or contact:
- Email: pamela@dasein.works


## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions professional

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

