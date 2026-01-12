import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main

class TestMain(unittest.TestCase):

    @patch("main.agent.invoke")
    def test_handle_chat_unified(self, mock_invoke):
        # Create a mock response that looks like a LangGraph State
        # It needs a 'messages' key containing message objects
        mock_ai_message = MagicMock()
        mock_ai_message.content = "This is the answer."
        
        mock_invoke.return_value = {
            "messages": [mock_ai_message]
        }

        result = main.handle_chat("Hello")
        self.assertEqual(result["answer"], "This is the answer.")
        mock_invoke.assert_called_once()

if __name__ == "__main__":
    unittest.main()