# Using LanceDB with Cloud Storage

LanceDB supports connecting to cloud storage such as AWS S3, Azure Blob Storage, or Google Cloud Storage. The `storage_options` parameter allows you to configure the authentication and other options needed to connect to these cloud storage services.

## Configuration

You can configure LanceDB to use cloud storage in the GraphRAG configuration file (`settings.yaml`):

```yaml
vector_store:
  default_vector_store:
    type: lancedb
    db_uri: s3://my-bucket/lancedb  # S3 URI
    storage_options:
      access_key: your_access_key
      secret_key: your_secret_key
      region: us-west-2
```

## Important: URI Format for Cloud Storage

When using cloud storage, the `db_uri` **must** start with the appropriate protocol prefix:

- **Azure Blob Storage**: `az://container/path`
- **AWS S3**: `s3://bucket/path`
- **Google Cloud Storage**: `gs://bucket/path`

If the URI does not start with one of these protocol prefixes, it will be treated as a local path and will be joined with the project's root directory.

## Storage Options for Different Cloud Providers

### AWS S3

```yaml
vector_store:
  default_vector_store:
    type: lancedb
    db_uri: s3://my-bucket/lancedb
    storage_options:
      access_key: your_access_key
      secret_key: your_secret_key
      region: us-west-2
```

### Azure Blob Storage

```yaml
vector_store:
  default_vector_store:
    type: lancedb
    db_uri: az://my-container/lancedb
    storage_options:
      account_name: your_account_name
      account_key: your_account_key
```

### Azure Blob Storage - Azurite Local Emulator

If you're using Azurite (the local emulator for Azure Storage), you'll need to use a different configuration:

```yaml
vector_store:
  default_vector_store:
    type: lancedb
    db_uri: az://container-name/path
    storage_options:
      connection_string: "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
```

Alternatively, you can use this format:

```yaml
vector_store:
  default_vector_store:
    type: lancedb
    db_uri: az://container-name/path
    storage_options:
      account_name: devstoreaccount1
      account_key: Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==
      endpoint_suffix: ""
      connection_string: ""
      custom_domain: "http://127.0.0.1:10000/devstoreaccount1"
```

### Google Cloud Storage

```yaml
vector_store:
  default_vector_store:
    type: lancedb
    db_uri: gs://my-bucket/lancedb
    storage_options:
      token: your_token  # or use other GCP authentication methods
```

## Runtime Usage

In code, you can connect to LanceDB with storage_options programmatically:

```python
from graphrag.vector_stores.lancedb import LanceDBVectorStore

# Configure storage options
storage_options = {
    "access_key": "your_access_key",
    "secret_key": "your_secret_key",
    "region": "us-west-2"
}

# Initialize vector store
vector_store = LanceDBVectorStore(collection_name="my_collection")
vector_store.connect(
    db_uri="s3://my-bucket/lancedb",  # Note the protocol prefix
    storage_options=storage_options
)
```

## Troubleshooting

If you see your cloud storage URI getting mangled (e.g., `/home/user/project/az://container/path`), make sure:

1. Your `db_uri` starts with the correct protocol prefix (`az://`, `s3://`, or `gs://`)
2. There are no extra spaces before the protocol prefix

### Azure Emulator Connection Issues

If you're getting errors with Azurite like:
```
RuntimeError: lance error: LanceError(IO): Generic MicrosoftAzure error
```

Try the following:

1. Make sure the container exists in your local Azurite instance
2. Try using the connection string approach instead of separate parameters
3. For Azurite, use `custom_domain` instead of `azure_endpoint`
4. Ensure Azurite is running and accessible at the specified endpoint

## Related Documentation

For more details on storage options supported by LanceDB, refer to:
- [LanceDB Documentation](https://lancedb.github.io/lancedb/)
- [fsspec Documentation](https://filesystem-spec.readthedocs.io/en/latest/) - LanceDB uses fsspec for cloud storage interfaces
- [adlfs Documentation](https://github.com/fsspec/adlfs) - The underlying library used for Azure Blob Storage 