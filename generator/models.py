from crum import get_current_user
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from django.utils.translation import gettext as _
from io import BytesIO
from PIL import Image

from clubs_and_events.settings import STORAGE_BASE_DIR
from community.models import Event, Community

import qrcode


class QRCode(models.Model):
    def get_image_path(self, file_name):
        return '{}/qr_code/{}'.format(STORAGE_BASE_DIR, file_name)

    url = models.CharField(max_length=255)
    image = models.ImageField(upload_to=get_image_path, blank=True)
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='qr_code_created_by')

    def __str__(self):
        return self.url

    def save(self, *args, **kwargs):
        qr_code_image = qrcode.make(self.url)
        canvas = Image.new('RGB', (qr_code_image.pixel_size, qr_code_image.pixel_size), 'white')
        canvas.paste(qr_code_image)
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.image.save('qr_code.png', File(buffer), save=False)
        canvas.close()

        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user

        super(QRCode, self).save(*args, **kwargs)


class JoinKey(models.Model):
    key = models.CharField(max_length=64, unique=True)
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='join_key_created_by')

    def clean(self):
        errors = list()

        valid_char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        for i in self.key:
            if i not in valid_char:
                errors.append(ValidationError(
                    _('Join keys must only contain alphabetical characters and numbers.'),
                    code='invalid_join_key'
                ))

        if len(errors) > 0:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user

        super(JoinKey, self).save(*args, **kwargs)
