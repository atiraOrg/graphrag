def test_cloud_storage_uris_not_modified():
    """Test that cloud storage URIs for LanceDB are not modified."""
    config = GraphRagConfig(
        root_dir="/home/user/project",
        vector_store={
            "local_store": VectorStoreConfig(
                type="lancedb",
                db_uri="local/path/to/db",
            ),
            "azure_store": VectorStoreConfig(
                type="lancedb",
                db_uri="az://container/path/to/db",
                storage_options={"account_name": "test", "account_key": "test-key"},
            ),
            "s3_store": VectorStoreConfig(
                type="lancedb",
                db_uri="s3://bucket/path/to/db",
                storage_options={"access_key": "test", "secret_key": "test-key"},
            ),
            "gcs_store": VectorStoreConfig(
                type="lancedb",
                db_uri="gs://bucket/path/to/db",
                storage_options={"token": "test-token"},
            ),
        },
    )
    
    # Run the validation
    config._validate_vector_store_db_uri()
    
    # Check that local path is modified to absolute path
    assert config.vector_store["local_store"].db_uri.startswith("/home/user/project")
    
    # Check that cloud storage URIs are not modified
    assert config.vector_store["azure_store"].db_uri == "az://container/path/to/db"
    assert config.vector_store["s3_store"].db_uri == "s3://bucket/path/to/db"
    assert config.vector_store["gcs_store"].db_uri == "gs://bucket/path/to/db" 