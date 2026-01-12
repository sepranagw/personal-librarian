import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingest import load_manifest, save_manifest, build_vector_db
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
    @patch("ingest.PyPDFLoader")
    @patch("ingest.Chroma")
    @patch("ingest.OpenAIEmbeddings")
    @patch("ingest.load_manifest")
    @patch("ingest.save_manifest")
    def test_build_vector_db_logic(self, mock_save, mock_load, mock_emb, mock_chroma, mock_pdf, mock_mtime, mock_listdir):
        # Setup: One new file, one existing file
        mock_listdir.return_value = ["new.pdf", "old.pdf"]
        mock_load.return_value = {"old.pdf": 2000.0}
        mock_mtime.side_effect = lambda x: 3000.0 if "new.pdf" in x else 2000.0
        
        # Mock Chroma Instance
        mock_db = MagicMock()
        mock_chroma.return_value = mock_db
        
        build_vector_db()
        
        # Verify only 'new.pdf' was processed
        self.assertEqual(mock_pdf.call_count, 1)
        mock_db.add_documents.assert_called_once()
        mock_save.assert_called_once()

class TestIngestMultiFormat(unittest.TestCase):

    @patch("ingest.UnstructuredExcelLoader")
    @patch("os.path.getmtime")
    @patch("os.listdir")
    @patch("ingest.load_manifest")
    @patch("ingest.Chroma")
    def test_excel_ingestion_path(self, mock_chroma, mock_load, mock_listdir, mock_mtime, mock_excel_loader):
        """Verify that .xlsx files trigger the UnstructuredExcelLoader."""
        # 1. Setup mocks
        mock_listdir.return_value = ["jobs_2025.xlsx"]
        mock_load.return_value = {} # Empty manifest
        mock_mtime.return_value = 123456789
        
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

if __name__ == "__main__":
    unittest.main()