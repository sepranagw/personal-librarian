import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from unittest.mock import patch, MagicMock
from tools import get_retriever_tool

class TestTools(unittest.TestCase):
    @patch("tools.Chroma")
    @patch("tools.OpenAIEmbeddings")
    def test_tool_definition(self, mock_embeddings, mock_chroma):
        # Mock Chroma and its retriever
        mock_db = MagicMock()
        mock_retriever = MagicMock()
        mock_db.as_retriever.return_value = mock_retriever
        mock_chroma.return_value = mock_db

        tool = get_retriever_tool()

        # Check Tool Metadata
        self.assertEqual(tool.name, "search_personal_docs")
        self.assertIn("user's uploaded files", tool.description)

        # Verify Chroma was initialized with the correct directory
        mock_chroma.assert_called_once()
        self.assertEqual(mock_chroma.call_args.kwargs['persist_directory'], "./db")

if __name__ == "__main__":
    unittest.main()