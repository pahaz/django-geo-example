from mimetypes import guess_type
from urllib.parse import unquote
import os
import posixpath

from django.http import HttpResponseRedirect, FileResponse, Http404
from django.core.files.storage import default_storage as storage


def _normpath(path):
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        _, part = os.path.splitdrive(part)
        _, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    return newpath


def serve_from_storage(request, path):
    path = posixpath.normpath(unquote(path))
    path = path.lstrip('/')
    newpath = _normpath(path)
    if path != newpath:
        return HttpResponseRedirect(newpath)

    content_type, encoding = guess_type(path)
    content_type = content_type or 'application/octet-stream'

    try:
        file = storage.open(path)
    except Exception:  # noqa
        raise Http404()
    response = FileResponse(file, content_type=content_type)
    # response["Last-Modified"] = http_date(statobj.st_mtime)
    response["Content-Length"] = storage.size(path)
    if encoding:
        response["Content-Encoding"] = encoding
    return response
