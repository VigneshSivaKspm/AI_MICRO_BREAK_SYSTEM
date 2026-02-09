# Contributing Guidelines

## Code Style

### Python
- Follow PEP 8 guidelines
- Use 4-space indentation
- Use type hints where applicable
- Add docstrings to all functions

### JavaScript
- Use ES6+ syntax
- Use camelCase for variables
- Add comments for complex logic

### SQL
- Use uppercase for keywords
- Use meaningful table/column names
- Add indexes for performance

## Git Workflow

1. Create feature branch: `git checkout -b feature/feature-name`
2. Commit changes: `git commit -m "Descriptive message"`
3. Push to branch: `git push origin feature/feature-name`
4. Create Pull Request

## Testing

### Unit Tests
```bash
pytest tests/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Coverage Report
```bash
pytest --cov=modules tests/
```

## Reporting Issues

Include:
- Environment (OS, Python version)
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error logs

## Code Review

- At least one approval required
- Must pass all tests
- No merge conflicts

## Documentation

- Update README for major changes
- Add docstrings to new functions
- Update API documentation

## Release Process

1. Update version in `config.py`
2. Update `CHANGELOG.md`
3. Create release tag
4. Run final tests
5. Deploy to production

---

Thank you for contributing!
