import os
import sys
import runpy
import warnings
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import personal_librarian.main as main


class TestMain(unittest.TestCase):

    def setUp(self):
        # Ensure each test starts with no cached agent.
        main._agent = None

    def tearDown(self):
        main._agent = None

    @patch("personal_librarian.main.create_agent")
    @patch("personal_librarian.main.get_retriever_tool")
    def test_get_agent_lazy_initialization(self, mock_get_retriever_tool, mock_create_agent):
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent

        agent_first = main.get_agent()
        agent_second = main.get_agent()

        self.assertIs(agent_first, mock_agent)
        self.assertIs(agent_second, mock_agent)
        mock_get_retriever_tool.assert_called_once()
        mock_create_agent.assert_called_once_with(main.model, [mock_get_retriever_tool.return_value])

    @patch("personal_librarian.main.get_agent")
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

    @patch("personal_librarian.main.get_agent")
    def test_handle_chat_without_sources(self, mock_get_agent):
        final_message = SimpleNamespace(content="Only answer")

        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [final_message]
        }
        mock_get_agent.return_value = mock_agent

        result = main.handle_chat("Hello")
        self.assertEqual(result["answer"], "Only answer")
        self.assertEqual(result["sources"], [])

    def test_main_block_functions_exist(self):
        """Test that main block functions exist and are callable."""
        # Verify the module has the expected functions
        self.assertTrue(hasattr(main, 'handle_chat'))
        self.assertTrue(hasattr(main, 'get_agent'))
        self.assertTrue(hasattr(main, 'main'))
        self.assertTrue(callable(main.handle_chat))
        self.assertTrue(callable(main.get_agent))
        self.assertTrue(callable(main.main))


class TestMainEntryPoint(unittest.TestCase):
    @patch("langchain_openai.ChatOpenAI")
    @patch("builtins.input", return_value="quit")
    @patch("builtins.print")
    def test_module_dunder_main_executes(self, mock_print, mock_input, mock_chat_openai):
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"'personal_librarian.main' found in sys.modules",
                category=RuntimeWarning,
            )
            runpy.run_module("personal_librarian.main", run_name="__main__")

        mock_print.assert_any_call("--- Unified LangChain Agent Active ---")

    @patch("personal_librarian.main.handle_chat")
    @patch("builtins.input", side_effect=["hello", "quit"])
    @patch("builtins.print")
    def test_main_entry_point_chat_success(
        self,
        mock_print,
        mock_input,
        mock_handle_chat,
    ):
        mock_handle_chat.return_value = {
            "answer": "Final answer",
            "sources": ["Retrieved from: search_personal_docs"],
        }

        main.main()

        mock_handle_chat.assert_called_once_with("hello")
        mock_print.assert_any_call("--- Unified LangChain Agent Active ---")
        mock_print.assert_any_call("\nWelcome to your Smart Agent Personal Assistant.")
        mock_print.assert_any_call("\nAgent: Final answer")
        mock_print.assert_any_call("Sources: ['Retrieved from: search_personal_docs']")

    @patch("personal_librarian.main.handle_chat")
    @patch("builtins.input", side_effect=["hello", "quit"])
    @patch("traceback.print_exc")
    @patch("builtins.print")
    def test_main_entry_point_chat_exception(
        self,
        mock_print,
        mock_print_exc,
        mock_input,
        mock_handle_chat,
    ):
        mock_handle_chat.side_effect = RuntimeError("boom")

        main.main()

        mock_print.assert_any_call("\nError: boom")
        mock_print_exc.assert_called_once()

    def test_main_entry_point_startup(self):
        """Test that the main entry point prints startup messages."""
        # Use the current Python interpreter (assumes venv is activated or dependencies are installed)
        python_exe = sys.executable
        result = subprocess.run(
            [python_exe, "-m", "personal_librarian.main"],
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
