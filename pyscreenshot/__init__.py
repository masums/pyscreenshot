from PIL import Image
import logging
from pyscreenshot import imcodec
from pyscreenshot.about import __version__
from pyscreenshot.loader import Loader, FailedBackendError
from pyscreenshot.procutil import run_in_childprocess
from pyscreenshot.idleutil import is_inside_idle


ADDITIONAL_IMPORTS = [FailedBackendError]

log = logging.getLogger(__name__)
log.debug('version=%s', __version__)


def childprocess_default_value():
    """IDLE has problem with multiprocessing.

    Therefore the default is False for childprocess if the program was
    started inside IDLE.
    """
    # return not is_inside_idle()
    return False


def _grab_simple(backend=None, bbox=None, filename=None):
    loader = Loader()
    loader.force(backend)
    backend_obj = loader.selected()
    return backend_obj.grab(bbox)


def _grab(childprocess, backend=None, bbox=None, filename=None):
    if bbox:
        x1, y1, x2, y2 = bbox
        if x2 <= x1:
            raise ValueError('bbox x2<=x1')
        if y2 <= y1:
            raise ValueError('bbox y2<=y1')
    if childprocess:
        log.debug('running "%s" in child process', backend)
        return run_in_childprocess(
            _grab_simple, imcodec.codec, backend, bbox, filename)
    else:
        return _grab_simple(backend, bbox, filename)


def grab(bbox=None, childprocess=None, backend=None):
    """Copy the contents of the screen to PIL image memory.

    :param bbox: optional bounding box (x1,y1,x2,y2)
    :param childprocess: pyscreenshot can cause an error,
            if it is used on more different virtual displays
            and back-end is not in different process.
            Some back-ends are always different processes: scrot, imagemagick
            The default is False if the program was started inside IDLE,
            otherwise it is True.
    :param backend: back-end can be forced if set (examples:scrot, wx,..),
                    otherwise back-end is automatic
    """
    if childprocess is None:
        childprocess = childprocess_default_value()
    return _grab(
        childprocess=childprocess, backend=backend, bbox=bbox)


def backends():
    """Back-end names as a list.

    :return: back-ends as string list
    """
    return Loader().all_names


def _backend_version(backend):
    loader = Loader()
    loader.force(backend)
    try:
        x = loader.selected()
        v = x.backend_version()
    except Exception:
        v = None
    return v


def backend_version(backend, childprocess=None):
    """Back-end version.

    :param backend: back-end (examples:scrot, wx,..)
    :param childprocess: see :py:func:`grab`
    :return: version as string
    """
    if childprocess is None:
        childprocess = childprocess_default_value()
    if not childprocess:
        return _backend_version(backend)
    else:
        return run_in_childprocess(_backend_version, None, backend)
