# Contributing to Mockachu

Thank you for your interest in contributing to Mockachu! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Installation for Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/sahzudin/mockachu.git
   cd mockachu
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev,gui]"
   ```

## Project Structure

```
mockachu/
├── mockachu/         # Main package
│   ├── generators/              # Data generators
│   ├── services/               # Core services
│   ├── ui/                     # Desktop application UI
│   ├── localization/           # Language support
│   └── res/                    # Resources and data files
├── tests/                      # Test suite
├── docs/                       # Documentation
├── app.py                      # Desktop app entry point
├── api_server.py              # API server entry point
└── requirements.txt           # Dependencies
```

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Write clear, self-documenting code
- Maximum line length: 88 characters (Black formatter)

### Testing
- Write tests for new features
- Run tests before submitting PRs:
  ```bash
  pytest
  ```

### Documentation
- Update README.md for user-facing changes
- Add docstrings for public functions and classes
- Update API documentation for endpoint changes

## How to Contribute

### Reporting Bugs
1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include:
   - Operating system and version
   - Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/logs

### Suggesting Features
1. Check existing feature requests
2. Use the feature request template
3. Describe:
   - The problem you're trying to solve
   - Your proposed solution
   - Alternative solutions considered
   - Additional context

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clear, focused commits
   - Include tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Run tests
   pytest
   
   # Run linting
   flake8 mockachu/
   black --check mockachu/
   
   # Test both GUI and API
   python app.py
   python api_server.py
   ```

5. **Submit the pull request**
   - Use a clear, descriptive title
   - Reference related issues
   - Describe your changes
   - Include screenshots for UI changes

## Adding New Generators

To add a new data generator:

1. **Create the generator file**
   ```python
   # mockachu/generators/my_generator.py
   from .generator import BaseGenerator, GeneratorActions
   
   class MyGenerator(BaseGenerator):
       def __init__(self):
           super().__init__()
           # Initialize your generator
   ```

2. **Register actions**
   ```python
   class MyGeneratorActions(GeneratorActions):
       MY_ACTION = "my_action"
   ```

3. **Add to available generators**
   Update `services/available_generators.py`

4. **Write tests**
   ```python
   # tests/test_my_generator.py
   def test_my_generator():
       # Test your generator
   ```

## Code of Conduct

### Guidelines
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Give constructive feedback
- Show empathy towards other contributors

### Unacceptable Behavior
- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing private information
- Other conduct considered inappropriate

## Getting Help

- **Documentation**: Check the README and docs/
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- Special thanks in documentation

Thank you for contributing to Mockachu! 🎉
