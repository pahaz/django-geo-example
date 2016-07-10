# based on https://github.com/django-nonrel/mongodb-engine/blob/
# 1314786975d3d17fb1a2e870dfba004158a5e431/django_mongodb_engine/storage.py
from urllib.parse import urljoin
import os

from django.core.exceptions import ImproperlyConfigured
from django.core.files import File
from django.core.files.storage import Storage
from django.utils.encoding import filepath_to_uri
from django.conf import settings
from gridfs import GridFS, NoFile, DEFAULT_CHUNK_SIZE
from mongoengine import connection

from .iowrapper import ToByteIOWrapper


_settings_prepared = False


def prepare_mongodb_settings():
    global _settings_prepared
    if _settings_prepared:
        return
    if not hasattr(settings, 'MONGODB_DATABASES'):
        raise ImproperlyConfigured("Missing `MONGODB_DATABASES` "
                                   "in settings.py")

    for alias, conn_settings in settings.MONGODB_DATABASES.items():
        connection.register_connection(alias, **conn_settings)
    _settings_prepared = True


def _get_subcollections(collection):
    """
    Returns all sub-collections of `collection`.
    """
    # XXX: Use the MongoDB API for this once it exists.
    for name in collection.database.collection_names():
        cleaned = name[:name.rfind('.')]
        if cleaned != collection.name and cleaned.startswith(collection.name):
            yield cleaned


class GridFSStorage(Storage):
    """
    GridFS Storage backend for Django.

    This backend aims to add a GridFS storage to upload files to
    using Django's file fields.

    For performance, the file hirarchy is represented as a tree of
    MongoDB sub-collections.

    (One could use a flat list, but to list a directory '/this/path/'
    we would have to execute a search over the whole collection and
    then filter the results to exclude those not starting by
    '/this/path' using that model.)

    :param location:
       (optional) Name of the top-level node that holds the files. This
       value of `location` is prepended to all file paths, so it works
       like the `location` setting for Django's built-in
       :class:`~django.core.files.storage.FileSystemStorage`.
    :param collection:
        Name of the collection the file tree shall be stored in.
        Defaults to 'storage'.
    :param database:
        Alias of the Django database to use. Defaults to 'default' (the
        default Django database).
    :param base_url:
        URL that serves the files in GridFS (for instance, through
        nginx-gridfs).
        Defaults to None (file not accessible through a URL).
    """
    default_encoding = 'utf-8'
    default_chunk_size = DEFAULT_CHUNK_SIZE

    def _new_file_default_kwargs(self):
        return {
            'encoding': self.default_encoding,
            'chunk_size': self.default_chunk_size,
        }

    def __init__(self, location='', collection='storage', database='default',
                 base_url=None):
        self.location = location.strip(os.sep)
        self.collection = collection
        self.database = database

        if base_url is None:
            base_url = settings.MEDIA_URL
        elif not base_url.endswith('/'):
            base_url += '/'

        if not self.collection:
            raise ImproperlyConfigured("'collection' may not be empty.")

        if base_url and not base_url.endswith('/'):
            raise ImproperlyConfigured("If set, 'base_url' must end with a "
                                       "slash.")
        self.base_url = base_url

    def _open(self, path, mode='rb'):
        """
        Returns a :class:`~gridfs.GridOut` file opened in `mode`, or
        raises :exc:`~gridfs.errors.NoFile` if the requested file
        doesn't exist and mode is not 'w'.
        """
        assert mode in ['rb', 'wb', 'w'], 'mode not in ["rb", "wb", "w"]'
        gridfs, filename = self._get_gridfs(path)
        try:
            return gridfs.get_last_version(filename)
        except NoFile:
            if 'w' in mode:
                kwargs = self._new_file_default_kwargs()
                return gridfs.new_file(filename=filename, **kwargs)
            else:
                raise

    def _save(self, path, content):
        """
        Saves `content` into the file at `path`.
        """
        if not isinstance(content, File):
            raise TypeError("You can .save() only django.File instance")
        _file = content.file
        try:
            content.file = ToByteIOWrapper(_file)
            gridfs, filename = self._get_gridfs(path)
            kwargs = self._new_file_default_kwargs()
            gridfs.put(content, filename=filename, **kwargs)
        finally:
            content.file = _file
        return path

    def delete(self, path):
        """
        Deletes the file at `path` if it exists.
        """
        gridfs, filename = self._get_gridfs(path)
        try:
            gridfs.delete(gridfs.get_last_version(filename=filename)._id)  # noqa: pylint: protected-access
        except NoFile:
            pass

    def exists(self, path):
        """
        Returns `True` if the file at `path` exists in GridFS.
        """
        gridfs, filename = self._get_gridfs(path)
        return gridfs.exists(filename=filename)

    def listdir(self, path):
        """
        Returns a tuple (folders, lists) that are contained in the
        folder `path`.
        """
        gridfs, filename = self._get_gridfs(path)
        assert not filename
        subcollections = _get_subcollections(gridfs._GridFS__collection)  # noqa pylint: protected-access
        return set(c.split('.')[-1] for c in subcollections), gridfs.list()

    def size(self, path):
        """
        Returns the size of the file at `path`.
        """
        gridfs, filename = self._get_gridfs(path)
        return gridfs.get_last_version(filename=filename).length

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urljoin(self.base_url, filepath_to_uri(name))

    def created_time(self, path):
        """
        Returns the datetime the file at `path` was created.
        """
        gridfs, filename = self._get_gridfs(path)
        return gridfs.get_last_version(filename=filename).upload_date

    def _get_gridfs(self, path):
        """
        Returns a :class:`~gridfs.GridFS` using the sub-collection for
        `path`.
        """
        assert _settings_prepared, 'Don`t called prepare_mongodb_settings()'
        path, filename = os.path.split(path)
        path = os.path.join(self.collection, self.location, path.strip(os.sep))
        collection_name = path.replace(os.sep, '.').strip('.')

        if not hasattr(self, '_db'):
            from mongoengine.connection import get_connection
            self._db = get_connection(self.database).database  # noqa: pylint: attribute-defined-outside-init

        return GridFS(self._db, collection_name), filename
