from unittest import TestCase
from io import BytesIO, StringIO
from datetime import datetime, timedelta
import os
import tempfile

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.crypto import get_random_string

from .gridfs import GridFSStorage, prepare_mongodb_settings
from .iowrapper import ToByteIOWrapper


def _read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()


class TestIOWrapper(TestCase):
    def test_bytesio(self):
        d = BytesIO(b'data')
        w = ToByteIOWrapper(d)
        self.assertEqual(w.read(), b'data')

    def test_stringio(self):
        d = StringIO('data')
        w = ToByteIOWrapper(d)
        self.assertEqual(w.read(), b'data')

    def test_bytesio_write(self):
        d = BytesIO()
        w = ToByteIOWrapper(d)
        w.write(b'data')
        w.seek(0)
        self.assertEqual(w.read(), b'data')

    def test_stringio_write(self):
        d = StringIO()
        w = ToByteIOWrapper(d)
        w.write('data')
        w.seek(0)
        self.assertEqual(w.read(), b'data')

    def test_stringio_readline(self):
        d = StringIO("line1\nline2")
        w = ToByteIOWrapper(d)
        self.assertEqual(w.readline(), b'line1\n')

    def test_stringio_readlines(self):
        d = StringIO("line1\nline2")
        w = ToByteIOWrapper(d)
        self.assertEqual(w.readlines(), [b'line1\n', b'line2'])

    def test_stringio_readinto(self):
        d = BytesIO(b"line1\nline2")
        w = ToByteIOWrapper(d)
        z = bytearray(17)
        self.assertEqual(w.readinto(z), 11)
        self.assertEqual(z, bytearray(b'line1\nline2\x00\x00\x00\x00\x00\x00'))


class GridFSStorageTest(TestCase):
    storage_class = GridFSStorage
    temp_dir = tempfile.mktemp()

    test_image = os.path.join(os.path.dirname(__file__), 'test_image.png')
    test_image_content = _read_bytes(test_image)

    def make_file(self):
        return SimpleUploadedFile(
            name='test_image.png', content=self.test_image_content,
            content_type='image/png'
        )

    def make_file_upload_data(self, name=None):
        return {
            'file': self.make_file(),
            'name': name or get_random_string(),
        }

    def setUp(self):
        self.storage = self.get_storage(self.temp_dir)

    def tearDown(self):
        if hasattr(self.storage, '_db'):
            for collection in self.storage._db.collection_names():  # noqa
                if not collection.startswith('system.'):
                    self.storage._db.drop_collection(collection)  # noqa

    def get_storage(self, location, **kwargs):
        return self.storage_class(location=location, **kwargs)

    def test_file_access_options(self):
        """
        Standard file access options are available, and work as
        expected.
        """
        self.assertFalse(self.storage.exists('storage_test'))
        f = self.storage.open('storage_test', 'w')
        f.write('storage contents')
        f.close()

        self.assertTrue(self.storage.exists('storage_test'))

        test_file = self.storage.open('storage_test', 'rb')
        self.assertEqual(test_file.read(), b'storage contents')

        self.storage.delete('storage_test')
        self.assertFalse(self.storage.exists('storage_test'))

    def test_file_created_time(self):
        """
        File storage returns a Datetime object for the creation time of
        a file.
        """
        self.assertFalse(self.storage.exists('test.file'))

        f = ContentFile('custom contents')
        f_name = self.storage.save('test.file', f)

        self.assertTrue(datetime.now() - self.storage.created_time(f_name) <
                        timedelta(seconds=2))
        self.storage.delete(f_name)

    def test_file_save_without_name(self):
        """
        File storage extracts the filename from the content object if
        no name is given explicitly.
        """
        self.assertFalse(self.storage.exists('test.file'))

        f = ContentFile('custom contents')
        f.name = 'test.file'

        storage_f_name = self.storage.save(None, f)

        self.assertEqual(storage_f_name, f.name)

        self.storage.delete(storage_f_name)

    def test_file_url(self):
        self.assertEqual(self.storage.url('test.file'), '/media/test.file')

    def test_listdir(self):
        """
        File storage returns a tuple containing directories and files.
        """
        self.assertEqual(self.storage.listdir(''), (set(), []))
        self.assertFalse(self.storage.exists('storage_test_1'))
        self.assertFalse(self.storage.exists('storage_test_2'))
        self.assertFalse(self.storage.exists('storage_dir_1'))

        self.storage.save('storage_test_1', ContentFile('custom content'))
        self.storage.save('storage_test_2', ContentFile('custom content'))
        storage = self.get_storage(
            location=os.path.join(self.temp_dir, 'storage_dir_1'))
        storage.save('storage_test_3', ContentFile('custom content'))

        dirs, files = self.storage.listdir('')
        self.assertEqual(set(dirs), {'storage_dir_1'})
        self.assertEqual(set(files), {'storage_test_1', 'storage_test_2'})

    def test_save_image(self):
        img = self.make_file()
        name = "/static/secret/" + img.name
        self.assertFalse(self.storage.exists(name))
        self.storage.save(name, img)
        self.assertTrue(self.storage.exists(name))
        f = self.storage.open(name)
        self.assertEqual(f.read(), self.test_image_content)


prepare_mongodb_settings()
