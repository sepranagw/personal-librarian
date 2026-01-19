import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingest import load_manifest, build_vector_db
import ingest


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
    @patch("os.path.exists")
    @patch("ingest.PyPDFLoader")
    @patch("ingest.FAISS")
    @patch("ingest.OpenAIEmbeddings")
    @patch("ingest.load_manifest")
    @patch("ingest.save_manifest")
    def test_build_vector_db_logic(self, mock_save, mock_load, mock_emb, mock_faiss, mock_pdf, mock_exists, mock_mtime, mock_listdir):
        # Setup: One new file, one existing file
        mock_listdir.return_value = ["new.pdf", "old.pdf"]
        mock_load.return_value = {"old.pdf": 2000.0}
        mock_mtime.side_effect = lambda x: 3000.0 if "new.pdf" in x else 2000.0
        mock_exists.return_value = False  # No existing FAISS index

        # Mock FAISS
        mock_db = MagicMock()
        mock_faiss.from_documents.return_value = mock_db

        build_vector_db()

        # Verify only 'new.pdf' was processed
        self.assertEqual(mock_pdf.call_count, 1)
        mock_db.save_local.assert_called_once()
        mock_save.assert_called_once()


class TestNoDataToIngest(unittest.TestCase):
    @patch("os.listdir")
    @patch("ingest.FAISS")
    @patch("builtins.print")
    def test_build_vector_db_logic(self, mock_print, mock_faiss, mock_listdir):
        mock_listdir.return_value = []


        build_vector_db()

        # Verify no new docs to be processed
        mock_print.assert_called_with("No new changes detected.")


class TestIngestExcelFormat(unittest.TestCase):

    @patch("ingest.UnstructuredExcelLoader")
    @patch("os.path.getmtime")
    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("ingest.load_manifest")
    @patch("ingest.FAISS")
    def test_excel_ingestion_path(self, mock_faiss, mock_load, mock_listdir, mock_exists, mock_mtime, mock_excel_loader):
        """Verify that .xlsx files trigger the UnstructuredExcelLoader."""
        # 1. Setup mocks
        mock_listdir.return_value = ["jobs_2025.xlsx"]
        mock_load.return_value = {}  # Empty manifest
        mock_mtime.return_value = 123456789
        mock_exists.return_value = False  # No existing FAISS index

        # Mock FAISS
        mock_db = MagicMock()
        mock_faiss.from_documents.return_value = mock_db

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

class TestIngestPowerpointFormat(unittest.TestCase):

    @patch("ingest.UnstructuredPowerPointLoader")
    @patch("os.path.getmtime")
    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("ingest.load_manifest")
    @patch("ingest.FAISS")
    def test_powerpoint_ingestion_path(self, mock_faiss, mock_load, mock_listdir, mock_exists, mock_mtime, mock_ppt_loader):
        """Verify that .pptx files trigger the UnstructuredPowerPointLoader."""
        # 1. Setup mocks
        mock_listdir.return_value = ["jobs_presentation.pptx"]
        mock_load.return_value = {}  # Empty manifest
        mock_mtime.return_value = 90909
        mock_exists.return_value = False  # No existing FAISS index

        # Mock FAISS
        mock_db = MagicMock()
        mock_faiss.from_documents.return_value = mock_db

        # Mock the loader instance and its .load() method
        mock_loader_inst = MagicMock()
        mock_text_doc = MagicMock()
        mock_text_doc.page_content = "Job hunt strategy, Networking is the most likely avenue for getting an interview"
        mock_text_doc.metadata = {"source": "jobs_presentation.pptx"}
    
        mock_image_doc = MagicMock()
        mock_image_doc.page_content = "[Image: Career networking diagram]"
        mock_image_doc.metadata = {
            "source": "jobs_presentation.pptx", 
            "element_type": "image",
            "slide_number": 1,
            "image_name": "networking_diagram.jpg"
        }

        mock_table_doc = MagicMock()
        mock_table_doc.page_content = "Top Companies | Hiring Status | Interview Stage\nGoogle | Active | Technical Round\nMicrosoft | Active | Final Round"
        mock_table_doc.metadata = {
            "source": "jobs_presentation.pptx",
            "element_type": "table", 
            "slide_number": 2
        }
        mock_loader_inst.load.return_value = [mock_text_doc, mock_image_doc, mock_table_doc]
        mock_ppt_loader.return_value = mock_loader_inst

        # 2. Run ingest
        ingest.build_vector_db()

        # 3. Assertions
        mock_ppt_loader.assert_called_once_with(os.path.join("./data", "jobs_presentation.pptx"), mode="elements")
        print("Powerpoint ingestion path verified.")

class TestIngestWordFormat(unittest.TestCase):

    @patch("ingest.Docx2txtLoader")
    @patch("os.path.getmtime")
    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("ingest.load_manifest")
    @patch("ingest.FAISS")
    def test_word_ingestion_path(self, mock_faiss, mock_load, mock_listdir, mock_exists, mock_mtime, mock_word_loader):
        """Verify that .docx files trigger the Docx2txtLoader."""
        # 1. Setup mocks
        mock_listdir.return_value = ["my_doc.docx"]
        mock_load.return_value = {}  # Empty manifest
        mock_mtime.return_value = 2222222
        mock_exists.return_value = False  # No existing FAISS index

        # Mock FAISS
        mock_db = MagicMock()
        mock_faiss.from_documents.return_value = mock_db

        # Mock the loader instance and its .load() method
        mock_loader_inst = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "Find the work records in alpha 5"
        mock_doc.metadata = {"source": "my_doc.docx"}
        mock_loader_inst.load.return_value = [mock_doc]
        mock_word_loader.return_value = mock_loader_inst

        # 2. Run ingest
        ingest.build_vector_db()

        # 3. Assertions
        mock_word_loader.assert_called_once_with(os.path.join("./data", "my_doc.docx"))
        print("Word doc ingestion path verified.")


class TestFAISSCreation(unittest.TestCase):
    """Test that FAISS.from_documents is called when vectorstore doesn't exist."""

    @patch("ingest.PyPDFLoader")
    @patch("os.path.getmtime")
    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("ingest.load_manifest")
    @patch("ingest.save_manifest")
    @patch("ingest.FAISS")
    @patch("ingest.OpenAIEmbeddings")
    def test_faiss_creation_from_documents(self, mock_emb, mock_faiss, mock_save, mock_load, mock_listdir, mock_exists, mock_mtime, mock_pdf_loader):
        """Verify that FAISS.from_documents is called when vectorstore is None."""
        # 1. Setup mocks
        mock_listdir.return_value = ["new_document.pdf"]
        mock_load.return_value = {}  # Empty manifest
        mock_mtime.return_value = 123456789
        
        # Key: os.path.exists returns False for FAISS_INDEX_PATH check (line 39 in ingest.py)
        # This makes vectorstore = None initially
        mock_exists.return_value = False
        
        # Mock the loader instance
        mock_loader_inst = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "Sample PDF content"
        mock_doc.metadata = {"source": "new_document.pdf"}
        mock_loader_inst.load.return_value = [mock_doc]
        mock_pdf_loader.return_value = mock_loader_inst
        
        # Mock FAISS
        mock_db = MagicMock()
        mock_faiss.from_documents.return_value = mock_db
        
        # 2. Run ingest
        ingest.build_vector_db()
        
        # 3. Assertions - verify from_documents was called (not add_documents)
        mock_faiss.from_documents.assert_called_once()
        # The first argument should be the filtered_chunks
        call_args = mock_faiss.from_documents.call_args
        self.assertIsNotNone(call_args)
        # Second argument should be embeddings
        self.assertEqual(call_args[0][1], mock_emb.return_value)
        print("FAISS creation from documents verified.")


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
