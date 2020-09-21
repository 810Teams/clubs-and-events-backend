from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from community.models import EmailPreference
from community.models import Profile

from community.models import Club
from community.models import Event
from community.models import CommunityEvent
from community.models import Lab

from community.models import Announcement
from community.models import Album
from community.models import AlbumImage
from community.models import Comment

from community.models import CustomMembershipLabel


class EmailPreferenceForm(forms.ModelForm):
    class Meta:
        model = EmailPreference
        exclude = []
        widgets = {}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'last_online', 'is_lecturer', 'email_preferences']
        widgets = {}

    def clean(self):
        data = super().clean()
        errors = list()

        # TODO: Validates Data

        if len(errors) > 0:
            raise errors


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        exclude = ['is_official']
        widgets = {}

    def clean(self):
        data = super().clean()
        errors = list()

        # TODO: Validates Data

        if len(errors) > 0:
            raise errors


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['status']
        widgets = {}

    def clean(self):
        data = super().clean()
        errors = list()

        # TODO: Validates Data

        if len(errors) > 0:
            raise errors


class CommunityEventForm(forms.ModelForm):
    class Meta:
        model = CommunityEvent
        exclude = ['status']
        widgets = {}

    def clean(self):
        data = super().clean()
        errors = list()

        # TODO: Validates Data

        if len(errors) > 0:
            raise errors


class LabForm(forms.ModelForm):
    class Meta:
        model = Lab
        exclude = []
        widgets = {}

    def clean(self):
        data = super().clean()
        errors = list()

        # TODO: Validates Data

        if len(errors) > 0:
            raise errors


# TODO: Complete Form
class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        exclude = ['created_datetime', 'community', 'creator']
        widgets = {}

        def clean(self):
            data = super().clean()
            errors = list()

            # TODO: Validates Data

            if len(errors) > 0:
                raise errors


# TODO: Complete Form
class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        exclude = ['created_datetime', 'community', 'creator']
        widgets = {}

        def clean(self):
            data = super().clean()
            errors = list()

            # TODO: Validates Data

            if len(errors) > 0:
                raise errors


# TODO: Complete Form
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['created_by', 'event']
        widgets = {}

        def clean(self):
            data = super().clean()
            errors = list()

            # TODO: Validates Data

            if len(errors) > 0:
                raise errors


# TODO: Complete Form
class CustomMembershipLabelForm(forms.ModelForm):
    class Meta:
        model = CustomMembershipLabel
        exclude = ['membership']
        widgets = {}

        def clean(self):
            data = super().clean()
            errors = list()

            # TODO: Validates Data

            if len(errors) > 0:
                raise errors


class LoginForm(forms.Form):
    username = forms.CharField(max_length=32, required=True)
    password = forms.CharField(max_length=256, required=True, widget=forms.PasswordInput())
