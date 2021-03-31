'''
    Membership Application Models
    membership/models.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from crum import get_current_request
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from clubs_and_events.settings import STORAGE_BASE_DIR
from community.models import Community, Lab, CommunityEvent, Club
from core.utils.general import get_file_extension, has_instance
from core.utils.objects import save_user_attributes
from user.permissions import IsStudentObject, IsLecturerObject


class Request(models.Model):
    ''' Request model '''
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

    def __str__(self):
        ''' String representation '''
        return '{}, {} ({})'.format(self.user.__str__(), self.community.__str__(), self.id)

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='user', updated_by_field_name='updated_by')
        super(Request, self).save(*args, **kwargs)

    def clean(self):
        ''' Validate on save '''
        errors = list()

        # User group verification
        if has_instance(self.community, Club):
            if not IsStudentObject().has_object_permission(get_current_request(), None, self.user):
                errors.append(ValidationError(_('Only students can request to join the club.'), code='restricted'))
        elif has_instance(self.community, Lab):
            if not IsStudentObject().has_object_permission(get_current_request(), None, self.user):
                if not IsLecturerObject().has_object_permission(get_current_request(), None, self.user):
                    errors.append(ValidationError(
                        _('Only students and lecturers can request to join the lab.'), code='restricted'
                    ))

        # Unable to request if the user is already a member
        memberships = Membership.objects.filter(status__in=('A', 'R'))
        if (self.user.id, self.community.id) in [(i.user.id, i.community.id) for i in memberships]:
            if self.status == 'W':
                errors.append(ValidationError(
                    _('The user is already a member of this community.'), code='already_member'
                ))

        # Unable to request if the user already has a pending request
        requests = Request.objects.filter(status='W')
        if self.id is not None:
            requests = requests.exclude(pk=self.id)
        if (self.user.id, self.community.id) in [(i.user.id, i.community.id) for i in requests]:
            if self.status == 'W':
                errors.append(ValidationError(_('Pending request from this user already exists.'), code='restricted'))

        # Unable to request if the user already has a pending invitation
        invitations = Invitation.objects.filter(status='W')
        if (self.user.id, self.community.id) in [(i.invitee.id, i.community.id) for i in invitations]:
            if self.status == 'W':
                errors.append(ValidationError(
                    _('Pending invitation to this user already exists.'), code='duplicated_invitation'
                ))

        if len(errors) > 0:
            raise ValidationError(errors)


class Invitation(models.Model):
    ''' Invitation model '''
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

    def __str__(self):
        ''' String representation '''
        return '{}, {}, {} ({})'.format(
            self.invitor.__str__(), self.invitee.__str__(), self.community.__str__(), self.id
        )

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='invitor', updated_by_field_name=None)
        super(Invitation, self).save(*args, **kwargs)

    def clean(self):
        ''' Validate on save '''
        errors = list()

        # User group verification
        if has_instance(self.community, Club):
            if not IsStudentObject().has_object_permission(get_current_request(), None, self.invitee):
                errors.append(ValidationError(_('Only students can be invited to the club.'), code='restricted'))
        elif has_instance(self.community, Lab):
            if not IsStudentObject().has_object_permission(get_current_request(), None, self.invitee):
                if not IsLecturerObject().has_object_permission(get_current_request(), None, self.invitee):
                    errors.append(ValidationError(
                        _('Only students and lecturers can be invited to the lab.'), code='restricted'
                    ))

        # Unable to invite if the user is already a member
        memberships = Membership.objects.filter(status__in=('A', 'R'))
        if (self.invitee.id, self.community.id) in [(i.user.id, i.community.id) for i in memberships]:
            if self.status == 'W':
                errors.append(ValidationError(
                    _('The user is already a member of this community.'), code='already_member'
                ))

        # Unable to invite if the user already has a pending request
        requests = Request.objects.filter(status='W')
        if (self.invitee.id, self.community.id) in [(i.user.id, i.community.id) for i in requests]:
            if self.status == 'W':
                errors.append(ValidationError(_('Pending request from this user already exists.'), code='restricted'))

        # Unable to invite if the user already has a pending invitation
        invitations = Invitation.objects.filter(status='W')
        if self.id is not None:
            invitations = invitations.exclude(pk=self.id)
        if (self.invitee.id, self.community.id) in [(i.invitee.id, i.community.id) for i in invitations]:
            if self.status == 'W':
                errors.append(ValidationError(
                    _('Pending invitation to this user already exists.'), code='duplicated_invitation'
                ))

        if len(errors) > 0:
            raise ValidationError(errors)


class Membership(models.Model):
    ''' Membership model '''
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
        ''' String representation '''
        return '{}, {}'.format(self.community.__str__(), self.user.__str__())

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')
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
        ''' Validate on save '''
        errors = list()

        # User group verification
        if has_instance(self.community, Club):
            if not IsStudentObject().has_object_permission(get_current_request(), None, self.user):
                errors.append(ValidationError(_('Only students can be invited to the club.'), code='restricted'))
        elif has_instance(self.community, Lab):
            if not IsStudentObject().has_object_permission(get_current_request(), None, self.user):
                if not IsLecturerObject().has_object_permission(get_current_request(), None, self.user):
                    errors.append(ValidationError(
                        _('Only students and lecturers can be invited to the lab.'), code='restricted'
                    ))

        # Duplicated membership validation
        memberships = Membership.objects.filter(user_id=self.user.id, community_id=self.community.id)
        if self.id is not None:
            memberships = memberships.exclude(pk=self.id)
        if len(memberships) > 0:
            errors.append(ValidationError(
                _('The membership of this user already exists in this community.'), code='duplicated_membership'
            ))

        if len(errors) > 0:
            raise ValidationError(errors)


class CustomMembershipLabel(models.Model):
    ''' Custom membership label model '''
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE)
    label = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='custom_membership_label_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='custom_membership_label_updated_by')

    def __str__(self):
        ''' String representation '''
        return '{}, {}'.format(self.membership.__str__(), self.label)

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')
        super(CustomMembershipLabel, self).save(*args, **kwargs)


class MembershipLog(models.Model):
    ''' Membership log model '''
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

    def __str__(self):
        ''' String representation '''
        return '{}, {}, {} ({})'.format(self.membership.__str__(), self.position, self.status, self.id)

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')
        super(MembershipLog, self).save(*args, **kwargs)


class Advisory(models.Model):
    ''' Advisory model '''
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

    def __str__(self):
        ''' String representation '''
        return '{}, {} ({})'.format(self.advisor.__str__(), self.community.__str__(), self.id)

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')
        super(Advisory, self).save(*args, **kwargs)

    def clean(self):
        ''' Validate instance on save '''
        errors = list()

        # User group verification
        if not IsLecturerObject().has_object_permission(get_current_request(), None, self.advisor):
            errors.append(ValidationError(_('Advisor must be a lecturer.'), code='invalid_advisor'))

        # Overlapping validation
        advisors = Advisory.objects.filter(community_id=self.community.id)
        if self.id is not None:
            advisors = advisors.exclude(pk=self.id)
        for i in advisors:
            if self.start_date <= i.end_date or i.start_date <= self.end_date:
                errors.append(ValidationError(_('Advisory time overlapped.'), code='advisory_overlap'))

        # Date validation
        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))
        
        # Community validation
        if has_instance(self.community, CommunityEvent):
            errors.append(ValidationError(
                _('Advisories are not applicable on community events.'),
                code='advisory_feature'
            ))
        elif has_instance(self.community, Lab):
            errors.append(ValidationError(_('Advisories are not applicable on labs.'), code='advisory_feature'))

        if len(errors) > 0:
            raise ValidationError(errors)


class ApprovalRequest(models.Model):
    ''' Approval request model '''
    def get_file_path(self, file_name):
        ''' Get file path '''
        return '{}/approval_request/{}.{}'.format(STORAGE_BASE_DIR, self.id, get_file_extension(file_name))

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
        ''' String representation '''
        return self.community.__str__()

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')

        if self.pk is None:
            saved_attached_file = self.attached_file
            self.attached_file = None
            super(ApprovalRequest, self).save(*args, **kwargs)
            self.attached_file = saved_attached_file

            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        super(ApprovalRequest, self).save(*args, **kwargs)
