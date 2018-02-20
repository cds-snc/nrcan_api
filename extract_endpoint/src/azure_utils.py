import enum
import io
import typing
from azure.storage import blob


class StorageCoordinates(typing.NamedTuple):
    account: str
    key: str
    container: str
    domain: typing.Optional[str]


class EnvVariables(enum.Enum):
    account = 'EXTRACT_ENDPOINT_STORAGE_ACCOUNT'
    key = 'EXTRACT_ENDPOINT_STORAGE_KEY'
    container = 'EXTRACT_ENDPOINT_CONTAINER'
    domain = 'EXTRACT_ENDPOINT_STORAGE_DOMAIN'


class DefaultVariables(enum.Enum):
    account = 'devstoreaccount1'
    key = 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=='
    container = 'endpoint'
    domain = None


def upload_stream_to_azure(coords: StorageCoordinates, stream: io.BytesIO, filename: str) -> bool:
    account, key, container, domain = coords
    azure_path = filename

    block_blob_service = blob.BlockBlobService(account_name=account, account_key=key, custom_domain=domain)
    block_blob_service.create_blob_from_stream(container, azure_path, stream)

    return azure_path in [blob.name for blob in block_blob_service.list_blobs(container)]
