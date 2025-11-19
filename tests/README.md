# Running Tests

This directory contains the automated tests for the chatbot server. The tests are written using `pytest` and are designed to ensure the reliability and correctness of the API endpoints.

## Prerequisites

- Python 3.8+
- The required dependencies installed (`pip install -r requirements.txt`)

## How to Run Tests

To run the full test suite, navigate to the root of the repository and run the following command:

```bash
pytest
```

For a more detailed output, use the `-v` (verbose) flag:

```bash
pytest -v
```

### Running Specific Tests

You can also run specific test files or even individual test cases:

```bash
# Run only the server tests
pytest tests/test_server.py

# Run only the tests for the /chat endpoint
pytest tests/test_server.py::TestChatEndpoint
```

### Test Coverage

To measure code coverage, you can use the `pytest-cov` plugin. First, install it:

```bash
pip install pytest-cov
```

Then, run the tests with the coverage flag:

```bash
pytest --cov=.
```

This will generate a coverage report in the terminal. For a more detailed HTML report, run:

```bash
pytest --cov=. --cov-report=html
```

You can then open `htmlcov/index.html` in your browser to view the report.
