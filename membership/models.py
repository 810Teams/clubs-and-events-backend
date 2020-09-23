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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_by')
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default='W')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_by')


class Invitation(models.Model):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Accepted'),
        ('D', 'Declined')
    )

    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    invitor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invitor')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitee')
    invited_datetime = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS, default='W')


class Advisory(models.Model):
    advisor = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

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
    ENDED_REASON = (
        ('L', 'Left'),
        ('R', 'Removed')
    )

    POSITIONS = (
        (3, 'Club President/President/Lab Supervisor'),
        (2, 'Club Vice-President/Vice-President/Lab Deputy Supervisor'),
        (1, 'Club Staff/Staff/Lab Helper'),
        (0, 'Club Member/Participator/Lab Member')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    position = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    ended_reason = models.CharField(max_length=1, choices=ENDED_REASON, null=True, blank=True)

    def clean(self):
        errors = list()
        print(self.end_date, self.ended_reason)

        if self.position not in (0, 1, 2, 3):
            errors.append(ValidationError(_('Position must be a number from 0 to 3.'), code='position_out_of_range'))

        if self.end_date and (self.start_date > self.end_date):
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        if not self.end_date and self.ended_reason or self.end_date and not self.ended_reason:
            errors.append(ValidationError(
                _('Ended date and ended reason must both present or be both null.'),
                code='mismatch_status'
            ))

        if len(errors) > 0:
            raise ValidationError(errors)


class CustomMembershipLabel(models.Model):
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE)
    custom_label = models.CharField(max_length=32)
