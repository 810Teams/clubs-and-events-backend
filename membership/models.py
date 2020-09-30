from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from community.models import Community, Lab, CommunityEvent
from user.models import User


class Request(models.Model):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Accepted'),
        ('D', 'Declined')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_user')
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default='W')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='request_updated_by')


class Invitation(models.Model):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Accepted'),
        ('D', 'Declined')
    )

    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    invitor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='invitation_invitor')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitation_invitee')
    status = models.CharField(max_length=1, choices=STATUS, default='W')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Advisory(models.Model):
    advisor = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='advisory_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='advisory_updated_by')

    def clean(self):
        errors = list()

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        try:
            if CommunityEvent.objects.get(pk=self.community):
                errors.append(ValidationError(
                    _('Advisories are not applicable on community events.'),
                    code='advisory_feature'
                ))
        except CommunityEvent.DoesNotExist:
            pass

        try:
            if Lab.objects.get(pk=self.community):
                errors.append(ValidationError(_('Advisories are not applicable on labs.'), code='advisory_feature'))
        except Lab.DoesNotExist:
            pass

        if len(errors) > 0:
            raise ValidationError(errors)


class Membership(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('R', 'Retired'),
        ('L', 'Left'),
        ('X', 'Removed')
    )

    POSITIONS = (
        (3, 'Leader'),
        (2, 'Deputy Leader'),
        (1, 'Staff'),
        (0, 'Member')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    position = models.IntegerField(default=0)
    status = models.CharField(max_length=1, choices=STATUS, default='A')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='membership_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='membership_updated_by')

    def clean(self):
        errors = list()

        if self.position not in (0, 1, 2, 3):
            errors.append(ValidationError(_('Position must be a number from 0 to 3.'), code='position_out_of_range'))

        if len(errors) > 0:
            raise ValidationError(errors)

    def __str__(self):
        return '{} of {}'.format(self.user.username, self.community.name_en)


class CustomMembershipLabel(models.Model):
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE)
    label = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='custom_membership_label_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='custom_membership_label_updated_by')
