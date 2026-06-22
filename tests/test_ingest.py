import os
import runpy
import warnings
import unittest
from unittest.mock import patch, MagicMock, mock_open

from personal_librarian.ingest import load_manifest, build_vector_db
import personal_librarian.ingest as ingest


@patch.dict(
    os.environ,
    {
        "PGVECTOR_CONNECTION": "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian",
        "PGVECTOR_COLLECTION": "personal_docs",
    },
    clear=False,
)
class TestIngest(unittest.TestCase):
    @patch("os.path.exists")
    def test_load_manifest_empty(self, mock_exists):
        mock_exists.return_value = False
        self.assertEqual(load_manifest(), {})

    @patch("builtins.open", new_callable=mock_open, read_data='{"file.pdf": 1.0}')
    @patch("os.path.exists")
    def test_load_manifest_data(self, mock_exists, mock_file):
        mock_exists.return_value = True
        self.assertEqual(load_manifest()["file.pdf"], 1.0)

    @patch("os.listdir")
    @patch("os.path.getmtime")
    @patch("personal_librarian.ingest.PyPDFLoader")
    @patch("personal_librarian.config.PGVector")
    @patch("personal_librarian.ingest.OpenAIEmbeddings")
    @patch("personal_librarian.ingest.load_manifest")
    @patch("personal_librarian.ingest.save_manifest")
    def test_build_vector_db_logic(
        self, mock_save, mock_load, mock_emb, mock_pgvector, mock_pdf,
        mock_mtime, mock_listdir
    ):
        # Setup: One new file, one existing file
        mock_listdir.return_value = ["new.pdf", "old.pdf"]
        mock_load.return_value = {"old.pdf": 2000.0}
        mock_mtime.side_effect = lambda x: 3000.0 if "new.pdf" in x else 2000.0

        # Mock PGVector
        mock_db = MagicMock()
        mock_pgvector.return_value = mock_db

        build_vector_db()

        # Verify only 'new.pdf' was processed
        self.assertEqual(mock_pdf.call_count, 1)
        mock_db.add_documents.assert_called_once()
        mock_save.assert_called_once()


@patch.dict(
    os.environ,
    {
        "PGVECTOR_CONNECTION": "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian",
        "PGVECTOR_COLLECTION": "personal_docs",
    },
    clear=False,
)
class TestNoDataToIngest(unittest.TestCase):
    @patch("os.listdir")
    @patch("personal_librarian.config.PGVector")
    @patch("builtins.print")
    def test_build_vector_db_logic(self, mock_print, mock_pgvector, mock_listdir):
        mock_listdir.return_value = []

        build_vector_db()

        # Verify no new docs to be processed
        mock_print.assert_called_with("No new changes detected.")


@patch.dict(
    os.environ,
    {
        "PGVECTOR_CONNECTION": "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian",
        "PGVECTOR_COLLECTION": "personal_docs",
    },
    clear=False,
)
class TestIngestExcelFormat(unittest.TestCase):

    @patch("personal_librarian.ingest.UnstructuredExcelLoader")
    @patch("os.path.getmtime")
    @patch("os.listdir")
    @patch("personal_librarian.ingest.load_manifest")
    @patch("personal_librarian.config.PGVector")
    def test_excel_ingestion_path(self, mock_pgvector, mock_load, mock_listdir, mock_mtime, mock_excel_loader):
        """Verify that .xlsx files trigger the UnstructuredExcelLoader."""
        # 1. Setup mocks
        mock_listdir.return_value = ["jobs_2025.xlsx"]
        mock_load.return_value = {}  # Empty manifest
        mock_mtime.return_value = 123456789

        # Mock PGVector
        mock_db = MagicMock()
        mock_pgvector.return_value = mock_db

        # Mock the loader instance and its .load() method
        mock_loader_inst = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "Google, Software Engineer, 2025-01-01"
        mock_doc.metadata = {"source": "jobs_2025.xlsx"}
        mock_loader_inst.load.return_value = [mock_doc]
        mock_excel_loader.return_value = mock_loader_inst

        # 2. Run ingest
        ingest.build_vector_db()

        # 3. Assertions
        mock_excel_loader.assert_called_once_with(os.path.join("./data", "jobs_2025.xlsx"), mode="elements")
        print("Excel ingestion path verified.")


@patch.dict(
    os.environ,
    {
        "PGVECTOR_CONNECTION": "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian",
        "PGVECTOR_COLLECTION": "personal_docs",
    },
    clear=False,
)
class TestIngestPowerpointFormat(unittest.TestCase):
    @patch("personal_librarian.ingest.UnstructuredPowerPointLoader")

    def test_powerpoint_ingestion_path(self, mock_ppt_loader):
        """Verify that .pptx files trigger the UnstructuredPowerPointLoader."""
        service = ingest.IngestionService(ingest.IngestConfig())
        file_path = os.path.join("./data", "jobs_presentation.pptx")
        mock_loader_inst = MagicMock()
        mock_ppt_loader.return_value = mock_loader_inst

        loader = service.yield_loader("jobs_presentation.pptx", file_path)

        self.assertIs(loader, mock_loader_inst)
        mock_ppt_loader.assert_called_once_with(
            file_path,
            mode="elements",
        )


@patch.dict(
    os.environ,
    {
        "PGVECTOR_CONNECTION": "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian",
        "PGVECTOR_COLLECTION": "personal_docs",
    },
    clear=False,
)
class TestIngestWordFormat(unittest.TestCase):
    @patch("personal_librarian.ingest.Docx2txtLoader")

    def test_word_ingestion_path(self, mock_word_loader):
        """Verify that .docx files trigger the Docx2txtLoader."""
        service = ingest.IngestionService(ingest.IngestConfig())
        file_path = os.path.join("./data", "my_doc.docx")
        mock_loader_inst = MagicMock()
        mock_word_loader.return_value = mock_loader_inst

        loader = service.yield_loader("my_doc.docx", file_path)

        self.assertIs(loader, mock_loader_inst)
        mock_word_loader.assert_called_once_with(file_path)


@patch.dict(
    os.environ,
    {
        "PGVECTOR_CONNECTION": "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian",
        "PGVECTOR_COLLECTION": "personal_docs",
    },
    clear=False,
)
class TestPGVectorIngestion(unittest.TestCase):
    """Test that chunks are added to PGVector during ingestion."""

    def test_pgvector_add_documents_called(self):
        """Verify that add_documents is called on PGVector."""
        service = ingest.IngestionService(ingest.IngestConfig())
        mock_loader_inst = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "Sample PDF content"
        mock_doc.metadata = {"source": "new_document.pdf"}
        mock_loader_inst.load.return_value = [mock_doc]
        mock_vectorstore = MagicMock()
        manifest = {}
        mtime = 123456789

        with patch.object(service, "chunk_and_filter_docs", return_value=["chunk"]):
            loaded, vectorstore, updated_manifest = service.load_new_docs(
                mock_loader_inst,
                "new_document.pdf",
                manifest,
                mtime,
                mock_vectorstore,
            )

        self.assertTrue(loaded)
        self.assertIs(vectorstore, mock_vectorstore)
        self.assertEqual(updated_manifest["new_document.pdf"], mtime)
        mock_vectorstore.add_documents.assert_called_once_with(["chunk"])


@patch.dict(
    os.environ,
    {
        "PGVECTOR_CONNECTION": "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian",
        "PGVECTOR_COLLECTION": "personal_docs",
    },
    clear=False,
)
class TestPGVectorConfigValidation(unittest.TestCase):
    @patch("personal_librarian.ingest.OpenAIEmbeddings")
    def test_build_vector_db_missing_pgvector_connection(self, mock_embeddings):
        with patch.dict(os.environ, {"PGVECTOR_CONNECTION": ""}, clear=False):
            with self.assertRaises(ValueError):
                ingest.build_vector_db()

    @patch("personal_librarian.ingest.OpenAIEmbeddings")
    def test_build_vector_db_missing_pgvector_collection(self, mock_embeddings):
        with patch.dict(os.environ, {"PGVECTOR_COLLECTION": ""}, clear=False):
            with self.assertRaises(ValueError):
                ingest.build_vector_db()


@patch.dict(
    os.environ,
    {
        "PGVECTOR_CONNECTION": "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian",
        "PGVECTOR_COLLECTION": "personal_docs",
    },
    clear=False,
)
class TestIngestionServiceBranches(unittest.TestCase):
    @patch("langchain_postgres.PGVector")
    def test_get_pgvector_store_with_config_override(self, mock_pgvector):
        config = ingest.IngestConfig(
            pgvector_connection="postgresql+psycopg://postgres:postgres@localhost:5432/custom_db",
            pgvector_collection="custom_collection",
        )
        service = ingest.IngestionService(config)
        embeddings = MagicMock()

        service.get_pgvector_store(embeddings)

        mock_pgvector.assert_called_once_with(
            embeddings=embeddings,
            collection_name="custom_collection",
            connection="postgresql+psycopg://postgres:postgres@localhost:5432/custom_db",
            use_jsonb=True,
        )

    def test_enrich_metadata_sets_source_page_and_date(self):
        config = ingest.IngestConfig()
        service = ingest.IngestionService(config)
        mock_doc = MagicMock()
        mock_doc.metadata = {
            "page_number": 3,
            "date": "2026-01-15",
        }

        enriched_docs = service.enrich_metadata(
            [mock_doc],
            "sample.pdf",
            "./data/sample.pdf",
            1700000000.0,
        )

        self.assertEqual(len(enriched_docs), 1)
        metadata = enriched_docs[0].metadata
        self.assertEqual(metadata["source_file"], "sample.pdf")
        self.assertEqual(metadata["source_path"], "./data/sample.pdf")
        self.assertEqual(metadata["source_type"], ".pdf")
        self.assertEqual(metadata["source"], "sample.pdf")
        self.assertEqual(metadata["page"], "3")
        self.assertEqual(metadata["doc_date"], "2026-01-15")
        self.assertIn("ingested_at", metadata)
        self.assertIn("source_mtime", metadata)


@patch.dict(
    os.environ,
    {
        "PGVECTOR_CONNECTION": "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian",
        "PGVECTOR_COLLECTION": "personal_docs",
    },
    clear=False,
)
class TestIngestEntryPoint(unittest.TestCase):
    @patch("personal_librarian.ingest.build_vector_db")
    @patch("builtins.print")
    def test_main_entry_point_prints_and_runs(
        self,
        mock_print,
        mock_build_vector_db,
    ):
        ingest.main()

        mock_print.assert_any_call("--- Starting Ingestion Process ---")
        mock_build_vector_db.assert_called_once()


@patch.dict(
    os.environ,
    {
        "PGVECTOR_CONNECTION": "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian",
        "PGVECTOR_COLLECTION": "personal_docs",
    },
    clear=False,
)
class TestIngestModuleDunderMain(unittest.TestCase):
    @patch("personal_librarian.config.PGVector")
    @patch("langchain_openai.OpenAIEmbeddings")
    @patch("os.listdir", return_value=[])
    @patch("builtins.print")
    def test_module_dunder_main_executes(
        self,
        mock_print,
        mock_listdir,
        mock_embeddings,
        mock_pgvector,
    ):
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"'personal_librarian.ingest' found in sys.modules",
                category=RuntimeWarning,
            )
            runpy.run_module("personal_librarian.ingest", run_name="__main__")

        mock_print.assert_any_call("--- Starting Ingestion Process ---")


# TODO: Re-enable in CI/CD pipeline where venv name is consistent
# class TestIngestMain(unittest.TestCase):
#     def test_main_entry_point(self):
#         """Test that the main entry point prints startup message and runs."""
#         # Use the current Python interpreter (assumes venv is activated or dependencies are installed)
#         python_exe = sys.executable
#         result = subprocess.run(
#             [python_exe, "ingest.py"],
#             capture_output=True,
#             text=True,
#             cwd=os.path.dirname(os.path.dirname(__file__))
#         )
#         # Check both stdout and stderr for the output (might go to either)
#         output = result.stdout + result.stderr

#         # Print for debugging if test fails
#         if "--- Starting Ingestion Process ---" not in output:
#             print(f"stdout: {result.stdout}")
#             print(f"stderr: {result.stderr}")
#             print(f"returncode: {result.returncode}")

#         self.assertIn("--- Starting Ingestion Process ---", output)


if __name__ == "__main__":
    unittest.main()
