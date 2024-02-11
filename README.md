# Ableton Assessment

## User Registration and Login Module

This module facilitates user registration and login, leveraging Python's capabilities for web service development and authentication handling.

### Prerequisites

Before proceeding, ensure the following requirements are met:

- Python 3 and pip are installed on your system.
- A `.env` file is created following the structure outlined in `.example.env`.

### Setup

Clone the repository to your local machine and navigate to the project directory.

## Development

### Starting the Development Server

To run the development server, execute:

```bash
python3 main.py
```

This command starts a local web server. Access the service at http://localhost:5000.

## Testing

### Running Tests and Generating Coverage Reports

1. Install dependencies

   ```bash
   pip3 install -r dev-requirements.txt
   ```

2. Execute Tests

   Run the tests using pytest and generate a coverage report:

   ```bash
   python3 -m pytest tests --cov-report html:report/pytest --cov "."
   ```

3. View Coverage Report

   Generate and display a summary of the test coverage in your terminal:

   ```bash
   coverage report
   ```

Alternatively, to streamline the process, you can chain these commands:

```bash
pip3 install -r dev-requirements.txt && python3 -m pytest tests --cov-report html:report/pytest --cov "." && coverage report
```

## Approach and Thought Process

The development of this module involved several key steps:

1. Researching Python 3 libraries for web server functionality.
2. Consulting resources and OpenAI's ChatGPT for guidance on specific topics, including:
   - Implementing authentication with http.server.
   - Utilizing dataclasses for data validation.
   - Hashing passwords securely.
3. Integrating the SQLite3 database for data persistence.
4. Adapting existing code examples to meet the module's requirements.
5. Writing comprehensive unit and integration tests to ensure reliability.
