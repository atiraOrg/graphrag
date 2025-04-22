#!/usr/bin/env python
"""
Test script for connecting to Azurite (local Azure Storage emulator) using LanceDB.

This script helps verify and debug connections to Azurite.
"""

import argparse
import logging
import os
import sys

# Add the project root to the path so we can import graphrag modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from graphrag.vector_stores.lancedb import LanceDBVectorStore

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection(container_name, path, storage_options):
    """Test connection to Azurite using LanceDB."""
    try:
        # Construct the URI in the format az://container/path
        db_uri = f"az://{container_name}/{path}"
        logger.info(f"Testing connection to: {db_uri}")
        logger.info(f"With storage options: {storage_options}")
        
        # Initialize vector store
        vector_store = LanceDBVectorStore(collection_name="test_collection")
        
        # Connect to LanceDB
        vector_store.connect(db_uri=db_uri, storage_options=storage_options)
        
        # Try to list tables to verify connection
        tables = vector_store.db_connection.table_names()
        logger.info(f"Connection successful! Available tables: {tables}")
        
        return True
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Azurite connection with LanceDB")
    parser.add_argument("--container", required=True, help="Container name")
    parser.add_argument("--path", default="lancedb", help="Path within container")
    
    # Azure connection options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--connection-string", help="Azure storage connection string")
    group.add_argument("--custom-domain", help="Custom domain for Azure emulator")
    
    args = parser.parse_args()
    
    storage_options = {}
    
    if args.connection_string:
        storage_options["connection_string"] = args.connection_string
    elif args.custom_domain:
        storage_options.update({
            "account_name": "devstoreaccount1",
            "account_key": "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
            "custom_domain": args.custom_domain,
            "endpoint_suffix": "",
        })
    
    success = test_connection(args.container, args.path, storage_options)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 