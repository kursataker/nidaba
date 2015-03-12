# -*- coding: utf-8 -*-
"""
nibada.tasks.img
~~~~~~~~~~~~~~

Some general image processing tasks that are outside the scope of more specific
packages (e.g. binarization).

"""

from __future__ import absolute_import, unicode_literals

from nibada import storage
from nibada import leper
from nibada import image
from nibada.celery import app
from nibada.tasks.helper import NibadaTask


@app.task(base=NibadaTask, name=u'nibada.img.rgb_to_gray')
def rgb_to_gray(doc, id, method=u'rgb_to_gray'):
    """
    Converts an arbitrary bit depth image to grayscale and writes it back
    appending a suffix.
    
    Args:
        doc (unicode, unicode): The input document tuple
        id (unicode): The nibada batch identifier this task is a part of
        method (unicode): The suffix string appended to all output files.

    Returns:
        (unicode, unicode): Storage tuple of the output file
    """
    input_path = storage.get_abs_path(*doc)
    output_path = storage.insert_suffix(input_path, method)
    return storage.get_storage_path(image.rgb_to_gray(input_path, output_path))

@app.task(base=NibadaTask, name=u'nibada.img.dewarp')
def dewarp(doc, id, method=u'dewarp'):
    """
    Removes perspective distortion (as commonly exhibited by overhead scans)
    from an 1bpp input image.
    
    Args:
        doc (unicode, unicode): The input document tuple.
        id (unicode): The nibada batch identifier this task is a part of
        method (unicode): The suffix string appended to all output files.

    Returns:
        (unicode, unicode): Storage tuple of the output file
    """
    input_path = storage.get_abs_path(*doc)
    output_path = storage.insert_suffix(input_path, method)
    return storage.get_storage_path(leper.dewarp(input_path, output_path))

@app.task(base=NibadaTask, name=u'nibada.img.deskew')
def deskew(doc, id, method=u'deskew'):
    """
    Removes skew (rotational distortion) from an 1bpp input image.
    
    Args:
        doc (unicode, unicode): The input document tuple.
        id (unicode): The nibada batch identifier this task is a part of
        method (unicode): The suffix string appended to all output files.

    Returns:
        (unicode, unicode): Storage tuple of the output file
    """
    input_path = storage.get_abs_path(*doc)
    output_path = storage.insert_suffix(input_path, method)
    return storage.get_storage_path(leper.deskew(input_path, output_path))
