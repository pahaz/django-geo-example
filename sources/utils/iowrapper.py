from django.core.files import File


class ToByteIOWrapper(File):
    default_encoding = 'utf-8'

    def read(self, size=-1):
        data = super().read(size)  # noqa
        if not isinstance(data, bytes):
            data = data.encode(self.default_encoding)
        return data

    def readline(self, size=-1):
        data = super().readline(size)  # noqa
        if not isinstance(data, bytes):
            data = data.encode(self.default_encoding)
        return data

    def readlines(self, hint=-1):
        data = super().readlines()  # noqa
        return [
            (x if isinstance(x, bytes) else x.encode(self.default_encoding))
            for x in data]

    def xreadlines(self, *args, **kwargs):
        raise NotImplementedError('xreadlines')
