import os
import unittest
from unittest.mock import patch, MagicMock

from personal_librarian.tools import get_retriever_tool


@patch.dict(
    os.environ,
    {
        "PGVECTOR_CONNECTION": "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian",
        "PGVECTOR_COLLECTION": "personal_docs",
    },
    clear=False,
)
class TestTools(unittest.TestCase):
    @patch("personal_librarian.config.PGVector")
    @patch("personal_librarian.tools.OpenAIEmbeddings")
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

    @patch("personal_librarian.config.PGVector")
    @patch("personal_librarian.tools.OpenAIEmbeddings")
    def test_tool_definition_missing_pgvector_connection(self, mock_embeddings, mock_pgvector):
        with patch.dict(os.environ, {"PGVECTOR_CONNECTION": ""}, clear=False):
            with self.assertRaises(ValueError):
                get_retriever_tool()

        mock_pgvector.assert_not_called()

    @patch("personal_librarian.config.PGVector")
    @patch("personal_librarian.tools.OpenAIEmbeddings")
    def test_tool_definition_missing_pgvector_collection(self, mock_embeddings, mock_pgvector):
        with patch.dict(os.environ, {"PGVECTOR_COLLECTION": ""}, clear=False):
            with self.assertRaises(ValueError):
                get_retriever_tool()

        mock_pgvector.assert_not_called()


if __name__ == "__main__":
    unittest.main()
