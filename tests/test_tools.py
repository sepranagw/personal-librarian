import os
import unittest
from unittest.mock import patch, MagicMock

from personal_librarian.tools import get_retriever_tool, get_retriever_tool_with_filter


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
    @patch("personal_librarian.tools.create_retriever_tool")
    @patch("personal_librarian.tools.OpenAIEmbeddings")
    def test_tool_definition(self, mock_embeddings, mock_create_tool, mock_pgvector):
        # Mock PGVector and its retriever
        mock_db = MagicMock()
        mock_retriever = MagicMock()
        mock_db.as_retriever.return_value = mock_retriever
        mock_pgvector.return_value = mock_db
        mock_tool = MagicMock()
        mock_tool.name = "search_personal_docs"
        mock_tool.description = "Use this tool to find information from the user's uploaded files and notes."
        mock_create_tool.return_value = mock_tool

        tool = get_retriever_tool()

        # Check Tool Metadata
        self.assertEqual(tool.name, "search_personal_docs")
        self.assertIn("user's uploaded files", tool.description)
        self.assertTrue(mock_create_tool.called)
        create_tool_kwargs = mock_create_tool.call_args.kwargs
        self.assertIn("document_prompt", create_tool_kwargs)

        # Verify PGVector was initialized
        mock_pgvector.assert_called_once()

    @patch("personal_librarian.config.PGVector")
    @patch("personal_librarian.tools.create_retriever_tool")
    @patch("personal_librarian.tools.OpenAIEmbeddings")
    def test_tool_definition_with_filter(self, mock_embeddings, mock_create_tool, mock_pgvector):
        mock_db = MagicMock()
        mock_retriever = MagicMock()
        mock_db.as_retriever.return_value = mock_retriever
        mock_pgvector.return_value = mock_db
        mock_create_tool.return_value = MagicMock()

        metadata_filter = {"source_file": "resume.pdf"}
        get_retriever_tool_with_filter(metadata_filter=metadata_filter, k=7)

        mock_db.as_retriever.assert_called_once_with(
            search_kwargs={"k": 7, "filter": metadata_filter}
        )
        self.assertTrue(mock_create_tool.called)

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
