'''
    Generator Application Models
    generator/models.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from django.utils.translation import gettext as _
from io import BytesIO
from PIL import Image

from clubs_and_events.settings import STORAGE_BASE_DIR
from community.models import Club, Event
from core.utils.objects import save_user_attributes
from generator.generate_docx import generate_docx

import os
import qrcode


class QRCode(models.Model):
    ''' QR code model '''
    def get_image_path(self, file_name):
        ''' Get image path '''
        return '{}/qr_code/{}'.format(STORAGE_BASE_DIR, file_name)

    url = models.CharField(max_length=255)
    image = models.ImageField(upload_to=get_image_path, blank=True)
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='qr_code_created_by')

    def __str__(self):
        ''' String representation '''
        return self.url

    def save(self, *args, **kwargs):
        ''' Save instance '''
        qr_code_image = qrcode.make(self.url)
        canvas = Image.new('RGB', (qr_code_image.pixel_size, qr_code_image.pixel_size), 'white')
        canvas.paste(qr_code_image)
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.image.save('qr_code.png', File(buffer), save=False)
        canvas.close()

        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name=None)

        super(QRCode, self).save(*args, **kwargs)


class JoinKey(models.Model):
    ''' Join key model '''
    key = models.CharField(max_length=64, unique=True)
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='join_key_created_by')

    def __str__(self):
        ''' String representation '''
        return self.event.name_en

    def clean(self):
        ''' Validate instance '''
        errors = list()

        if not self.key.isalnum():
            errors.append(ValidationError(
                _('Join keys must only contain alphabetical characters and numbers.'), code='invalid_join_key'
            ))

        if len(errors) > 0:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name=None)
        super(JoinKey, self).save(*args, **kwargs)


class GeneratedDocx(models.Model):
    ''' Generated Microsoft Word document model '''
    def get_file_path(self, file_name):
        ''' Get file path '''
        return '{}/generated_docx/{}/{}'.format(STORAGE_BASE_DIR, self.club.id, file_name)

    # Main Field
    club = models.OneToOneField(Club, on_delete=models.CASCADE)

    # Fill-in Fields
    advisor = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=False)
    objective = models.TextField(max_length=512)
    objective_list = models.TextField(max_length=1024)
    room = models.CharField(max_length=32)
    schedule = models.CharField(max_length=128)
    plan_list = models.TextField(max_length=1024)
    merit = models.TextField(max_length=1024)

    # Generated Field
    document = models.FileField(upload_to=get_file_path)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='docx_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='docx_updated_by')

    def __str__(self):
        ''' String representation '''
        return self.club.name_en

    def save(self, *args, **kwargs):
        ''' Save instance '''
        buffer = BytesIO()

        # Template selection
        if not self.club.is_official:
            template_file_name = 'form-club-creation-template.docx'
            generated_file_name = 'generated-form-club-creation.docx'
        else:
            template_file_name = 'form-club-renewal-template.docx'
            generated_file_name = 'generated-form-club-renewal.docx'

        # Save an empty file as a path for model
        self.document.save(
            generated_file_name,
            File(buffer),
            save=False
        )

        # Save an actual Microsoft Word document file
        generate_docx(
            template_file_name,
            existing_docx=self.document,
            club=self.club,
            advisor=self.advisor,
            objective=self.objective,
            objective_list=self.objective_list,
            room=self.room,
            schedule=self.schedule,
            plan_list=self.plan_list,
            merit=self.merit,
            save=True
        )

        # Save updaters
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')

        # Save
        super(GeneratedDocx, self).save(*args, **kwargs)
