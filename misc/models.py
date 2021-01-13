'''
    Miscellaneous Application Models
    misc/models.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from django.db import models

from clubs_and_events.settings import STORAGE_BASE_DIR
from core.utils.general import truncate, get_file_extension
from core.utils.objects import save_user_attributes


class FAQ(models.Model):
    ''' Frequently asked question (FAQ) model '''
    def get_image_path(self, file_name):
        ''' Retrieve image path '''
        return '{}/faq/{}.{}'.format(STORAGE_BASE_DIR, self.id, get_file_extension(file_name))

    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=2048)
    image = models.ImageField(null=True, blank=True, upload_to=get_image_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='faq_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='faq_updated_by')

    def __str__(self):
        ''' String representation '''
        return '{}'.format(truncate(self.question, max_length=32))

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')

        if self.pk is None:
            saved_image = self.image
            self.image = None
            super(FAQ, self).save(*args, **kwargs)
            self.image = saved_image

            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        super(FAQ, self).save(*args, **kwargs)
