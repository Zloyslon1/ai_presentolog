# Tests

This directory contains all test files and test-related documentation for AI Presentolog.

## Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for system workflows
├── debug/          # Debug utilities and scripts
└── docs/           # Test documentation and guides
```

## Unit Tests

Located in `unit/`, these tests verify individual components:

- **test_content_analyzer.py** - Tests for content analysis functions
- **test_text_splitter.py** - Tests for text splitting logic
- **test_local.py** - Local environment and configuration tests
- **test_api_key.py** - API key validation tests
- **test_service_account.py** - Service account authentication tests

## Integration Tests

Located in `integration/`, these tests verify end-to-end workflows and component interactions.

## Debug Utilities

Located in `debug/`, these are helper scripts for debugging and troubleshooting:

- **check_db.py** - Database inspection utility
- **debug_design.py** - Design template debugging
- **debug_titles.py** - Title extraction debugging

## Test Documentation

Located in `docs/`, these documents describe testing procedures and scenarios:

- Testing guides
- Multi-user testing scenarios
- Authentication testing procedures

## Running Tests

### Run all unit tests:
```bash
python -m pytest tests/unit/
```

### Run specific test:
```bash
python tests/unit/test_content_analyzer.py
```

### Run debug scripts:
```bash
python tests/debug/check_db.py
```

## Contributing

When adding new features, please:
1. Add unit tests to `unit/`
2. Add integration tests to `integration/` if applicable
3. Update test documentation in `docs/`
4. Ensure all tests pass before committing

## Notes

- Test files follow the naming convention: `test_*.py`
- Debug scripts are meant for development use only
- All tests should be independent and repeatable
# Tests

This directory contains all test files and test-related documentation for AI Presentolog.

## Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for system workflows
├── debug/          # Debug utilities and scripts
└── docs/           # Test documentation and guides
```

## Unit Tests

Located in `unit/`, these tests verify individual components:

- **test_content_analyzer.py** - Tests for content analysis functions
- **test_text_splitter.py** - Tests for text splitting logic
- **test_local.py** - Local environment and configuration tests
- **test_api_key.py** - API key validation tests
- **test_service_account.py** - Service account authentication tests

## Integration Tests

Located in `integration/`, these tests verify end-to-end workflows and component interactions.

## Debug Utilities

Located in `debug/`, these are helper scripts for debugging and troubleshooting:

- **check_db.py** - Database inspection utility
- **debug_design.py** - Design template debugging
- **debug_titles.py** - Title extraction debugging

## Test Documentation

Located in `docs/`, these documents describe testing procedures and scenarios:

- Testing guides
- Multi-user testing scenarios
- Authentication testing procedures

## Running Tests

### Run all unit tests:
```bash
python -m pytest tests/unit/
```

### Run specific test:
```bash
python tests/unit/test_content_analyzer.py
```

### Run debug scripts:
```bash
python tests/debug/check_db.py
```

## Contributing

When adding new features, please:
1. Add unit tests to `unit/`
2. Add integration tests to `integration/` if applicable
3. Update test documentation in `docs/`
4. Ensure all tests pass before committing

## Notes

- Test files follow the naming convention: `test_*.py`
- Debug scripts are meant for development use only
- All tests should be independent and repeatable
