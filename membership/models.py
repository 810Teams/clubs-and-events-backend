from crum import get_current_user
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from community.models import Community, Lab, CommunityEvent, Club
from clubs_and_events.settings import STORAGE_BASE_DIR


class Request(models.Model):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Accepted'),
        ('D', 'Declined')
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='request_user')
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default='W')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='request_updated_by')

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.user = user
        self.updated_by = user

        super(Request, self).save(*args, **kwargs)


class Invitation(models.Model):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Accepted'),
        ('D', 'Declined')
    )

    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    invitor = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='invitation_invitor')
    invitee = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='invitation_invitee')
    status = models.CharField(max_length=1, choices=STATUS, default='W')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.invitor = user

        super(Invitation, self).save(*args, **kwargs)


class Advisory(models.Model):
    advisor = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='advisory_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='advisory_updated_by')

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        super(Advisory, self).save(*args, **kwargs)

    def clean(self):
        errors = list()

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        try:
            if CommunityEvent.objects.get(pk=self.community.id):
                errors.append(ValidationError(
                    _('Advisories are not applicable on community events.'),
                    code='advisory_feature'
                ))
        except CommunityEvent.DoesNotExist:
            pass

        try:
            if Lab.objects.get(pk=self.community.id):
                errors.append(ValidationError(_('Advisories are not applicable on labs.'), code='advisory_feature'))
        except Lab.DoesNotExist:
            pass

        if len(errors) > 0:
            raise ValidationError(errors)


class Membership(models.Model):
    POSITION = (
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
    )

    STATUS = (
        ('A', 'Active'),
        ('R', 'Retired'),
        ('L', 'Left'),
        ('X', 'Removed')
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='membership_user')
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    position = models.IntegerField(choices=POSITION, default=0)
    status = models.CharField(max_length=1, choices=STATUS, default='A')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='membership_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='membership_updated_by')

    def __str__(self):
        return '{} - {}'.format(self.user.username, self.community.name_en)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        super(Membership, self).save(*args, **kwargs)

        logs = MembershipLog.objects.filter(membership_id=self.id)
        if len(logs) > 0:
            log = logs[len(logs) - 1]
            if log.position != self.position or log.status != self.status:
                log.end_datetime = timezone.now()
                log.save()
                MembershipLog.objects.create(membership_id=self.id, position=self.position, status=self.status)
        else:
            MembershipLog.objects.create(membership_id=self.id, position=self.position, status=self.status)


    def clean(self):
        errors = list()

        if self.position not in (0, 1, 2, 3):
            errors.append(ValidationError(_('Position must be a number from 0 to 3.'), code='position_out_of_range'))

        if len(errors) > 0:
            raise ValidationError(errors)


class CustomMembershipLabel(models.Model):
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE)
    label = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='custom_membership_label_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='custom_membership_label_updated_by')

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        super(CustomMembershipLabel, self).save(*args, **kwargs)


class MembershipLog(models.Model):
    POSITION = (
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
    )

    STATUS = (
        ('A', 'Active'),
        ('R', 'Retired'),
        ('L', 'Left'),
        ('X', 'Removed')
    )

    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    position = models.IntegerField(choices=POSITION, default=0)
    status = models.CharField(max_length=1, choices=STATUS, default='A')
    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='membership_log_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='membership_log_updated_by')

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        super(MembershipLog, self).save(*args, **kwargs)


class ApprovalRequest(models.Model):
    def get_file_path(self, file_name):
        return '{}/approval_request/{}/{}'.format(STORAGE_BASE_DIR, self.id, file_name)

    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Accepted'),
        ('D', 'Declined')
    )

    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    message = models.CharField(max_length=255, null=True, blank=True)
    attached_file = models.FileField(upload_to=get_file_path, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default='W')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approval_request_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approval_request_updated_by')

    def __str__(self):
        return self.community.name_en

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        super(ApprovalRequest, self).save(*args, **kwargs)
