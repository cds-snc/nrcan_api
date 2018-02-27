import os
import base64
import secrets
import typing
import datetime
import requests
import click
from extract_endpoint import crypt_utils


DEFAULT_ENDPOINT_SECRET_KEY = 'no key'


@click.group()
def main() -> None:
    pass


def post_stream(stream: typing.IO[bytes],
                filename: typing.Optional[str],
                url: str,
                timestamp: str) -> requests.models.Response:
    if filename is None and stream.name == '<stdin>':
        raise ValueError("Must supply a filename if reading from stdin")
    if filename is None:
        filename = stream.name

    data = stream.read()
    salt = secrets.token_hex(16)
    signature = crypt_utils.sign_string(salt=salt,
                                        key=os.environ.get('ENDPOINT_SECRET_KEY', DEFAULT_ENDPOINT_SECRET_KEY),
                                        data=base64.b64encode(data).decode('utf-8'))

    return requests.post(url=url,
                         files={'file': data},
                         data={'salt': salt, 'signature': signature, 'filename': filename, 'timestamp': timestamp})


@main.command()
@click.argument('stream', type=click.File('rb'))
@click.option('--filename')
@click.option('--url', default='http://127.0.0.1:5000/upload_file')
@click.option('--timestamp', default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
def upload(stream: typing.IO[bytes], filename: typing.Optional[str], url: str, timestamp: str) -> None:
    click.echo(str(post_stream(stream=stream, filename=filename, url=url, timestamp=timestamp)))
