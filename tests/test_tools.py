import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import get_retriever_tool  # noqa: E402


class TestTools(unittest.TestCase):
    @patch("tools.FAISS")
    @patch("tools.OpenAIEmbeddings")
    @patch("os.path.exists")
    def test_tool_definition(self, mock_exists, mock_embeddings, mock_faiss):
        # Mock path exists
        mock_exists.return_value = True

        # Mock FAISS and its retriever
        mock_db = MagicMock()
        mock_retriever = MagicMock()
        mock_db.as_retriever.return_value = mock_retriever
        mock_faiss.load_local.return_value = mock_db

        tool = get_retriever_tool()

        # Check Tool Metadata
        self.assertEqual(tool.name, "search_personal_docs")
        self.assertIn("user's uploaded files", tool.description)

        # Verify FAISS was loaded
        mock_faiss.load_local.assert_called_once()


if __name__ == "__main__":
    unittest.main()
