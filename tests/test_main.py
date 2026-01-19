import os
import sys
import subprocess
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main


class TestMain(unittest.TestCase):

    @patch("main.get_agent")
    def test_handle_chat_unified(self, mock_get_agent):
        # Create a mock response that looks like a LangGraph State
        # It needs a 'messages' key containing message objects
        mock_ai_message = MagicMock()
        mock_ai_message.content = "This is the answer."
        mock_ai_message.name = "search_personal_docs"
        
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [mock_ai_message]
        }
        mock_get_agent.return_value = mock_agent

        result = main.handle_chat("Hello")
        self.assertEqual(result["answer"], "This is the answer.")
        self.assertEqual(result["sources"], ["Retrieved from: search_personal_docs"])
        mock_agent.invoke.assert_called_once()

    @patch('builtins.input', side_effect=['exit'])
    @patch('builtins.print')
    @patch('main.handle_chat')
    def test_main_block_coverage(self, mock_handle_chat, mock_print, mock_input):
        """Test main block prints startup messages - for coverage tracking."""
        # Execute the if __name__ == "__main__" block by running the module code
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')) as f:
            code = compile(f.read(), 'main.py', 'exec')
        exec(code, {'__name__': '__main__'})

        # Verify startup messages were printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Unified LangChain Agent Active" in str(c) for c in print_calls))
        self.assertTrue(any("Welcome to your Smart Agent Personal Assistant" in str(c) for c in print_calls))


# TODO: Re-enable in CI/CD pipeline where venv name is consistent
class TestMainEntryPoint(unittest.TestCase):
    def test_main_entry_point_startup(self):
        """Test that the main entry point prints startup messages."""
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


if __name__ == "__main__":
    unittest.main()
