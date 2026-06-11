import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import get_retriever_tool  # noqa: E402


class TestTools(unittest.TestCase):
    @patch("tools.PGVector")
    @patch("tools.OpenAIEmbeddings")
    def test_tool_definition(self, mock_embeddings, mock_pgvector):
        # Mock PGVector and its retriever
        mock_db = MagicMock()
        mock_retriever = MagicMock()
        mock_db.as_retriever.return_value = mock_retriever
        mock_pgvector.return_value = mock_db

        tool = get_retriever_tool()

        # Check Tool Metadata
        self.assertEqual(tool.name, "search_personal_docs")
        self.assertIn("user's uploaded files", tool.description)

        # Verify PGVector was initialized
        mock_pgvector.assert_called_once()


if __name__ == "__main__":
    unittest.main()
