# Contributing to RabbitHole

Thank you for your interest in contributing to **RabbitHole**, an autonomous AI-driven honeypot.

## Development Standards (Google SRE Compliance)

To maintain the high-integrity and security standards of this project, all contributions must adhere to the following guidelines:

### 1. Code Style
*   **Python:** Follow [PEP 8](https://peps.python.org/pep-0008/) and the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
*   **Type Hinting:** All new functions and methods **must** include Python type hints (PEP 484).
*   **Docstrings:** Use the **Google Docstring Format** for all functions and classes.
    ```python
    def example_function(param1: int, param2: str) -> bool:
        """Example function description.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            True if successful, False otherwise.
        """
        return True
    ```

### 2. Security Mandates
*   **No Hardcoded Secrets:** Never commit API keys, tokens, or passwords. Use environment variables.
*   **Rootless Execution:** All containers and scripts must run as a non-privileged user (e.g., UID 10001).
*   **Input Validation:** All external input (attacker commands) must be treated as hostile.

### 3. Testing
*   Run the "Ultimate Test Suite" before submitting PRs:
    ```bash
    python3 ultimate_test.py
    ```
*   Ensure the `botnet_surge.py` benchmark maintains >200 connections/sec.

### 4. Pull Request Process
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes.
4.  Run tests.
5.  Open a Pull Request.

## License
By contributing, you agree that your contributions will be licensed under the Apache License, Version 2.0.
