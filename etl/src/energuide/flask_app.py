import os
import typing
from http import HTTPStatus
import hashlib
import flask
import pymongo
from energuide import database
from energuide import cli
from energuide import logger


LOGGER = logger.get_logger(__name__)


App = flask.Flask(__name__)


DEFAULT_ETL_SECRET_KEY = 'no key'

App.config.update(dict(
    SECRET_KEY=os.environ.get('ETL_SECRET_KEY', DEFAULT_ETL_SECRET_KEY),
))


DATABASE_COORDS = database.DatabaseCoordinates(
    username=os.environ.get(database.EnvVariables.username.value, default=database.EnvDefaults.username.value),
    password=os.environ.get(database.EnvVariables.password.value, default=database.EnvDefaults.password.value),
    host=os.environ.get(database.EnvVariables.host.value, default=database.EnvDefaults.host.value),
    port=int(os.environ.get(database.EnvVariables.port.value, default=database.EnvDefaults.port.value))
)

DATABASE_NAME = os.environ.get(database.EnvVariables.database.value, default=database.EnvDefaults.database.value)

COLLECTION = os.environ.get(database.EnvVariables.collection.value, default=database.EnvDefaults.collection.value)


@App.route('/', methods=['GET'])
def frontend() -> str:
    return ''


@App.route('/test_alive', methods=['GET'])
def test_alive() -> str:
    return 'Alive!'


@App.route('/robots933456.txt', methods=['GET'])
def robots() -> None:
    flask.abort(HTTPStatus.NOT_FOUND)


@App.route('/run_tl', methods=['POST'])
def run_tl() -> typing.Tuple[str, int]:
    if 'salt' not in flask.request.form:
        LOGGER.warning("request missing salt")
        return 'no salt', HTTPStatus.BAD_REQUEST
    if 'signature' not in flask.request.form:
        LOGGER.warning("request missing signature")
        return 'no signature', HTTPStatus.BAD_REQUEST

    salt = flask.request.form['salt']
    signature = flask.request.form['signature']
    hasher = hashlib.new('sha3_256')
    hasher.update((salt + App.config['SECRET_KEY']).encode())
    salt_signature = hasher.hexdigest()
    if salt_signature != signature:
        LOGGER.warning("request contained incorrect signature")
        return 'bad signature', HTTPStatus.BAD_REQUEST

    cli.load.callback(username=DATABASE_COORDS.username,
                      password=DATABASE_COORDS.password,
                      host=DATABASE_COORDS.host,
                      port=DATABASE_COORDS.port,
                      db_name=DATABASE_NAME,
                      collection=COLLECTION,
                      azure=True,
                      filename=None,
                      append=False,
                      progress=False)

    mongo_client: pymongo.MongoClient
    with database.mongo_client(DATABASE_COORDS) as mongo_client:
        records_created = mongo_client[DATABASE_NAME][COLLECTION].count()
    if records_created == 0:
        LOGGER.warning('error, no records created')
        return 'error, no records created', HTTPStatus.BAD_GATEWAY
    LOGGER.info(f'success, {records_created} created')
    return f'success, {records_created} created', HTTPStatus.CREATED


if __name__ == "__main__":
    App.run(host='0.0.0.0', port=5010)
