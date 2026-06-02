# Contributing to Dart Game Pro

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, browser)

### Suggesting Features

Feature requests are welcome! Please open an issue and:
- Describe the feature clearly
- Explain the use case
- Reference similar features in other apps if applicable

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and under 50 lines where possible

### Testing

- Run tests before submitting: `pytest tests/`
- Add tests for new features
- Ensure all existing tests pass

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues when applicable

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Dart-app.git
cd Dart-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run main.py

# Run tests
pytest tests/
```

## Questions?

Feel free to open an issue for any questions.
