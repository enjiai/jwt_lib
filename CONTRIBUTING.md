# Contributing to enjilib-jwt-auth

Thank you for your interest in contributing to enjilib-jwt-auth! This library is critical to Enji's authentication infrastructure, so we maintain high standards for code quality, testing, and documentation.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- `uv` package manager (recommended) or `pip`

### Environment Setup

1. **Clone the repository** (if working on a fork):
   ```bash
   git clone <repository-url>
   cd enjilib-jwt-auth
   ```

2. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies in development mode**:
   ```bash
   # Using uv (recommended)
   uv sync --all-extras
   
   # Or using pip
   pip install -e ".[dev]"
   ```

## Running Tests

All contributions must include test coverage. Token verification is security-critical.

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=enjilib_jwt --cov-report=term-missing

# Run specific test file
pytest tests/test_authenticator.py -v

# Run tests matching a pattern
pytest -k "verify" -v
```

**Coverage Requirement**: The project enforces 100% code coverage. All PRs touching token verification, encryption, or authorization logic must maintain this threshold.

## Code Standards

### Style Guide

- **Python**: Follow [PEP 8](https://pep8.org/) with a line length of 88 characters (Black formatter)
- **Type Hints**: All functions must include type hints
- **Docstrings**: Use Google-style docstrings for public APIs
- **Naming**: 
  - Classes: `PascalCase` (e.g., `JWTAuthenticator`)
  - Functions/variables: `snake_case` (e.g., `verify_and_extract`)
  - Constants: `UPPER_CASE` (e.g., `DEFAULT_ALGORITHM`)

### Token Compatibility Checklist

**This is a JWT authentication library.** All changes affecting token verification or format are breaking changes.

Before submitting a PR that touches token handling:

- [ ] Verify you understand the [Token Contract](./API.md#token-structure)
- [ ] Document how your change affects token verification, encryption, or structure
- [ ] Include tests covering both existing and new token formats (if applicable)
- [ ] If breaking: update `CHANGELOG.md` and set PR type to "Feature (breaking change)"
- [ ] Explain migration path for consumers (e.g., "Clients must update their token generation")

### Packaging Changes

**Dependencies and package metadata changes require maintainer approval.**

If your PR modifies:
- `pyproject.toml` (new/removed dependencies)
- `setup.py` (build configuration)
- `py.typed` marker (type hint distribution)
- Version number (in metadata)

Then:
1. Add a section explaining the change to your PR description
2. Request review from `@enjiai/maintainers`
3. Ensure all tests pass before merging

## Creating a Pull Request

### Before You Start

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes in focused, atomic commits
3. Ensure all tests pass locally: `pytest tests/`
4. Verify coverage: `pytest --cov=enjilib_jwt --cov-fail-under=100`

### PR Template

When you open a PR, use the [pull request template](./.github/pull_request_template.md).

**Key sections**:

- **Summary**: Concise description of the change
- **Token Contract Impact**: Mandatory disclosure — indicate None/Minor/Breaking
- **Package Metadata Changes**: Mandatory disclosure if dependencies or metadata changed
- **Testing & Verification**: Confirm all tests pass, coverage maintained
- **Documentation Updates**: List any README, API.md, or CHANGELOG.md changes

### PR Checklist

Your PR must satisfy:

- [ ] All tests pass locally: `pytest tests/` ✅
- [ ] Coverage maintained at 100%: `pytest --cov=enjilib_jwt --cov-fail-under=100` ✅
- [ ] Code follows project style guide (PEP 8, type hints, docstrings)
- [ ] PR description filled out completely (use the template)
- [ ] If token-related: token contract impact documented and tested
- [ ] If packaging-related: maintainer approval requested

## Review Process

### Who Reviews

PRs are reviewed by the Enji maintainers:
- `@enjiai/maintainers` — primary reviewers
- Security-sensitive changes may involve additional security team review

### Approval Criteria

A PR is approved when:

1. **All tests pass** — GitHub Actions CI must show green ✅
2. **Coverage maintained** — Project enforces 100% coverage on `enjilib_jwt`
3. **Code review passes** — At least one maintainer approves
4. **Token contract verified** — If applicable, token compatibility explained and tested
5. **Packaging approved** — If dependencies/metadata changed, maintainer explicitly approves
6. **Documentation updated** — Changes to behavior require README, API.md, or CHANGELOG.md updates

### Review Timelines

- **Bugfixes**: 1-2 business days
- **Features**: 2-3 business days
- **Security issues**: Expedited (contact `security@enjiai.org`)

## Documentation

### When to Update Docs

- **README.md**: Update if changing installation, usage examples, or public API
- **API.md**: Update when adding/changing public classes or methods
- **CHANGELOG.md**: Update for all public releases and breaking changes
- **Docstrings**: Inline comments for complex token verification logic

### Example Docstring

```python
def verify_and_extract(self, token: str) -> Optional[JWTClaims]:
    """
    Verify a JWT token and extract claims.
    
    Args:
        token: The JWT token string to verify.
    
    Returns:
        JWTClaims object if token is valid, None if verification fails.
    
    Raises:
        ValueError: If token format is invalid (before signature check).
    """
```

## Security Considerations

This is an authentication library. Security is paramount.

### Before Submitting

- [ ] Review your changes for timing attacks (especially in comparison operations)
- [ ] Verify that keys/secrets are never logged or printed
- [ ] Ensure exception messages don't leak sensitive information
- [ ] Test with examples from API.md documentation

### Reporting Security Issues

**Do not open GitHub issues for security vulnerabilities.** See [SECURITY.md](./SECURITY.md) for responsible disclosure.

## Questions?

- Check [API.md](./API.md) for token contract details
- Review existing tests in `tests/` for examples
- Open a GitHub Discussion or contact `@enjiai/maintainers`

---

Thank you for contributing! 🙏
