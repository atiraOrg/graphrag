# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Integration tests for LanceDB vector store implementation."""

import shutil
import tempfile
from unittest.mock import patch, MagicMock

import numpy as np

from graphrag.vector_stores.base import VectorStoreDocument
from graphrag.vector_stores.lancedb import LanceDBVectorStore


def test_vector_store_operations():
    """Test basic vector store operations with LanceDB."""
    # Create a temporary directory for the test database
    temp_dir = tempfile.mkdtemp()
    try:
        vector_store = LanceDBVectorStore(collection_name="test_collection")
        vector_store.connect(db_uri=temp_dir)

        docs = [
            VectorStoreDocument(
                id="1",
                text="This is document 1",
                vector=[0.1, 0.2, 0.3, 0.4, 0.5],
                attributes={"title": "Doc 1", "category": "test"},
            ),
            VectorStoreDocument(
                id="2",
                text="This is document 2",
                vector=[0.2, 0.3, 0.4, 0.5, 0.6],
                attributes={"title": "Doc 2", "category": "test"},
            ),
            VectorStoreDocument(
                id="3",
                text="This is document 3",
                vector=[0.3, 0.4, 0.5, 0.6, 0.7],
                attributes={"title": "Doc 3", "category": "test"},
            ),
        ]
        vector_store.load_documents(docs[:2])

        assert vector_store.collection_name in vector_store.db_connection.table_names()

        doc = vector_store.search_by_id("1")
        assert doc.id == "1"
        assert doc.text == "This is document 1"

        assert doc.vector is not None
        assert np.allclose(doc.vector, [0.1, 0.2, 0.3, 0.4, 0.5])
        assert doc.attributes["title"] == "Doc 1"

        filter_query = vector_store.filter_by_id(["1"])
        assert filter_query == "id in ('1')"

        results = vector_store.similarity_search_by_vector(
            [0.1, 0.2, 0.3, 0.4, 0.5], k=2
        )

        # Check we get expected number of results
        assert len(results) == 2

        # Check they're in the right order (by similarity)
        assert results[0].document.id == "1"
        assert results[1].document.id == "2"

        # Make sure scores are in descending order
        assert results[0].score > results[1].score

        # Add one more document without overwriting
        vector_store.load_documents([docs[2]], overwrite=False)

        # Should be 3 documents now
        results = vector_store.similarity_search_by_vector(
            [0.3, 0.4, 0.5, 0.6, 0.7], k=3
        )
        assert len(results) == 3
        assert results[0].document.id == "3"
    finally:
        # Clean up - remove the temporary directory
        shutil.rmtree(temp_dir)


def test_empty_collection():
    """Test creating an empty collection."""
    # Create a temporary directory for the test database
    temp_dir = tempfile.mkdtemp()
    try:
        vector_store = LanceDBVectorStore(collection_name="empty_collection")
        vector_store.connect(db_uri=temp_dir)

        # Load the vector store with a document, then delete it
        sample_doc = VectorStoreDocument(
            id="tmp",
            text="Temporary document to create schema",
            vector=[0.1, 0.2, 0.3, 0.4, 0.5],
            attributes={"title": "Tmp"},
        )
        vector_store.load_documents([sample_doc])
        vector_store.db_connection.open_table(vector_store.collection_name).delete(
            "id = 'tmp'"
        )

        # Should still have the collection
        assert vector_store.collection_name in vector_store.db_connection.table_names()

        # Add a document after creating an empty collection
        doc = VectorStoreDocument(
            id="1",
            text="This is document 1",
            vector=[0.1, 0.2, 0.3, 0.4, 0.5],
            attributes={"title": "Doc 1"},
        )
        vector_store.load_documents([doc], overwrite=False)

        result = vector_store.search_by_id("1")
        assert result.id == "1"
        assert result.text == "This is document 1"
    finally:
        # Clean up - remove the temporary directory
        shutil.rmtree(temp_dir)


def test_filter_search():
    """Test filtered search with LanceDB."""
    # Create a temporary directory for the test database
    temp_dir = tempfile.mkdtemp()
    try:
        vector_store = LanceDBVectorStore(collection_name="filter_collection")
        vector_store.connect(db_uri=temp_dir)

        # Create test documents with different categories
        docs = [
            VectorStoreDocument(
                id="1",
                text="Document about cats",
                vector=[0.1, 0.2, 0.3, 0.4, 0.5],
                attributes={"category": "animals"},
            ),
            VectorStoreDocument(
                id="2",
                text="Document about dogs",
                vector=[0.2, 0.3, 0.4, 0.5, 0.6],
                attributes={"category": "animals"},
            ),
            VectorStoreDocument(
                id="3",
                text="Document about cars",
                vector=[0.3, 0.4, 0.5, 0.6, 0.7],
                attributes={"category": "vehicles"},
            ),
        ]
        vector_store.load_documents(docs)

        # Filter to include only documents about animals
        vector_store.filter_by_id(["1", "2"])
        results = vector_store.similarity_search_by_vector(
            [0.1, 0.2, 0.3, 0.4, 0.5], k=3
        )

        # Should return at most 2 documents (the filtered ones)
        assert len(results) <= 2
        ids = [result.document.id for result in results]
        assert "3" not in ids
        assert set(ids).issubset({"1", "2"})
    finally:
        # Clean up - remove the temporary directory
        shutil.rmtree(temp_dir)


def test_storage_options():
    """Test LanceDB with storage_options parameter."""
    # Mock lancedb.connect to verify storage_options are passed correctly
    with patch("lancedb.connect") as mock_connect:
        # Setup mock connection
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        mock_db.table_names.return_value = []
        
        # Create test storage options
        storage_options = {
            "access_key": "test_access_key",
            "secret_key": "test_secret_key",
            "region": "us-west-2"
        }
        
        # Initialize vector store with mock
        vector_store = LanceDBVectorStore(collection_name="cloud_storage_test")
        vector_store.connect(
            db_uri="s3://my-test-bucket/lancedb", 
            storage_options=storage_options
        )
        
        # Verify connect was called with correct parameters
        mock_connect.assert_called_once_with(
            uri="s3://my-test-bucket/lancedb", 
            storage_options=storage_options
        )
