"""
System tests that require OPENAI_API_KEY and test the full application flow.

These tests make real API calls and test end-to-end functionality.
Run only when OPENAI_API_KEY is available.

Usage:
    python -m pytest tests/test_system.py -v
"""
import os
import sys
import subprocess
import unittest
from dotenv import load_dotenv

load_dotenv()


class TestMainEntryPoint(unittest.TestCase):
    """System test for the main application entry point."""

    @unittest.skipIf(
        not os.environ.get("OPENAI_API_KEY"),
        "OPENAI_API_KEY not set - skipping system test"
    )
    def test_main_entry_point_startup(self):
        """Test that the main entry point prints startup messages and runs with real API."""
        # Use the current Python interpreter (assumes venv is activated or dependencies are installed)
        python_exe = sys.executable
        result = subprocess.run(
            [python_exe, "main.py"],
            capture_output=True,
            text=True,
            input="exit\n",  # Provide input to exit immediately
            cwd=os.path.dirname(os.path.dirname(__file__)),
            timeout=30  # Prevent hanging
        )
        # Check both stdout and stderr for the output (might go to either)
        output = result.stdout + result.stderr

        # Print for debugging if test fails
        if "--- Unified LangChain Agent Active ---" not in output:
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            print(f"returncode: {result.returncode}")

        # Assert startup messages appear
        self.assertIn("--- Unified LangChain Agent Active ---", output)
        self.assertIn("Welcome to your Smart Agent Personal Assistant", output)

    @unittest.skipIf(
        not os.environ.get("OPENAI_API_KEY"),
        "OPENAI_API_KEY not set - skipping system test"
    )
    def test_main_exception_handling(self):
        """Test that main.py properly handles and displays exceptions."""
        python_exe = sys.executable

        env = os.environ.copy()
        # Use an unreachable host/port to force fast connection failure.
        env["PGVECTOR_CONNECTION"] = (
            "postgresql+psycopg://postgres:postgres@127.0.0.1:1/personal_librarian?connect_timeout=1"
        )

        result = subprocess.run(
            [python_exe, "main.py"],
            capture_output=True,
            text=True,
            input="What is in my documents?\nexit\n",
            cwd=os.path.dirname(os.path.dirname(__file__)),
            timeout=30,
            env=env,
        )

        output = result.stdout + result.stderr

        self.assertIn("Error:", output, "Expected error handling output when PGVector connection fails")


if __name__ == "__main__":
    unittest.main()
