'''
    Core Application File and Image Utility Functions
    core/utils/files.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.core.files import File
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage

from PIL import Image

from clubs_and_events.settings import DO_IMAGE_DOWNSCALING


def get_file_size(file):
    ''' Get file size '''
    if isinstance(file, File):
        return '{}'.format(simplify_file_size(file.size))
    raise ValueError


def get_image_size(image):
    ''' Get image size and dimensions '''
    if isinstance(image, ImageFile):
        return '{} ({}x{})'.format(simplify_file_size(image.size), image.width, image.height)
    raise ValueError


def simplify_file_size(size, unit='B'):
    ''' Simplify file size '''
    if unit == 'b' and size >= 8:
        size /= 8
        unit = 'B'
    if unit == 'B' and size >= 1024:
        size /= 1024
        unit = 'kB'
    if unit == 'kB' and size >= 1024:
        size /= 1024
        unit = 'MB'
    if unit == 'MB' and size >= 1024:
        size /= 1024
        unit = 'GB'
    if unit == 'GB' and size >= 1024:
        size /= 1024
        unit = 'TB'

    if unit == 'b':
        return '{} bits'.format(int(size))
    elif unit == 'B':
        return '{} bytes'.format(int(size))
    return '{:.2f} {}'.format(int(size * 100) / 100, unit)


def auto_downscale_image(image, threshold=(1024, 1024), round_function=round):
    ''' Downscale image size for storage space saving complete function for easy usage '''
    if DO_IMAGE_DOWNSCALING:
        try:
            downscale_image(
                image, threshold=threshold, round_function=round_function
            )
        except (ValueError, FileNotFoundError):
            pass


def downscale_image(image_in, threshold=(1024, 1024), round_function=round):
    ''' Downscale image size for storage space saving '''
    image = Image.open(image_in)

    width_ratio = image.width / threshold[0]
    height_ratio = image.height / threshold[1]

    if width_ratio > 1 or height_ratio > 1:
        if width_ratio > height_ratio:
            downscale_ratio = threshold[0] / image.width
        else:
            downscale_ratio = threshold[1] / image.height

        image = image.resize(
            (round_function(image.width * downscale_ratio), round_function(image.height * downscale_ratio)),
            Image.ANTIALIAS
        )

        storage_access = default_storage.open(image_in.name, 'wb')
        image_format = image_in.name.split('.')[-1]
        if image_format.lower() == 'jpg':
            image_format = 'jpeg'
        image.save(storage_access, image_format)
        storage_access.close()
