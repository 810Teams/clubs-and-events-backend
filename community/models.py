from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

# Group 1 - User
#   - Profile
#   - EmailPreference
#   - StudentCommitteeAuthority

class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    nickname = models.CharField(max_length=32, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(null=True, blank=True)
    cover_photo = models.ImageField(null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    last_online = models.DateTimeField(null=True, blank=True)
    is_lecturer = models.BooleanField()

    def __str__(self):
        return '{}'.format(self.user.username)


class EmailPreference(models.Model):
    receive_own_club = models.BooleanField(default=True)
    receive_own_event = models.BooleanField(default=True)
    receive_own_lab = models.BooleanField(default=True)
    receive_other_events = models.BooleanField(default=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.profile.user.username)


class StudentCommitteeAuthority(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return '{}'.format(self.profile.user.username)

    def clean(self):
        errors = list()

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        if len(errors) > 0:
            raise ValidationError(errors)


# Group 2 - Types
#   - ClubType
#   - EventType
#   - EventSeries

class ClubType(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)

    def __str__(self):
        return '{}'.format(self.title_en)


class EventType(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)

    def __str__(self):
        return '{}'.format(self.title_en)


class EventSeries(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)

    def __str__(self):
        return '{}'.format(self.title_en)


# Group 3 - Community
#   - Community
#   - Club
#   - Event
#   - CommunityEvent
#   - Lab

class Community(models.Model):
    name_th = models.CharField(max_length=64, unique=True)
    name_en = models.CharField(max_length=64, unique=True)
    url_id = models.CharField(max_length=16, null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)
    banner = models.ImageField(null=True, blank=True)
    is_publicly_visible = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.name_en)


class Club(Community):
    STATUS = (
        ('R', 'Recruiting'),
        ('C', 'Closed'),
        ('D', 'Disbanded'),
    )

    club_type = models.ForeignKey(ClubType, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.CharField(max_length=32, null=True, blank=True)
    founded_date = models.DateField()
    is_official = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=STATUS, default='R')

    def clean(self):
        errors = list()

        if not self.is_official:
            if self.room != None or len(self.room) > 0:
                errors.append(ValidationError(
                    _('Unofficial clubs are not able to occupy a room.'),
                    code='unofficial_club_limitations'
                ))
            if self.url_id != None or len(self.url_id) > 0:
                errors.append(ValidationError(
                    _('Unofficial clubs are not able to set custom URL ID.'),
                    code='unofficial_club_limitations'
                ))

        if len(errors) > 0:
            raise ValidationError(errors)


class Event(Community):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Approved'),
        ('C', 'Cancelled'),
    )

    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True, blank=True)
    event_series = models.ForeignKey(EventSeries, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=256)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=1, choices=STATUS, default='W')

    def clean(self):
        errors = list()

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        if len(errors) > 0:
            raise ValidationError(errors)


class CommunityEvent(Event):
    created_under = models.ForeignKey(Community, on_delete=models.PROTECT)
    allows_outside_participators = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self._meta.get_field('status').default = 'A'

    def clean(self):
        errors = list()

        if self.id == self.created_under.id:
            errors.append(ValidationError(
                _('Community events are not able to be created under its parent self.'),
                code='hierarchy_error'
            ))

        try:
            if Event.objects.get(pk=self.created_under.id) != None:
                errors.append(ValidationError(
                    _('Community events are not able to be created under events.'),
                    code='hierarchy_error'
                ))
        except Event.DoesNotExist:
            pass

        try:
            if Club.objects.get(pk=self.created_under.id) and not Club.objects.get(pk=self.created_under.id).is_official:
                errors.append(ValidationError(
                    _('Community events are not able to be created under unofficial clubs.'),
                    code='unofficial_club_limitations'
                ))
        except Club.DoesNotExist:
            pass

        if self.status == 'W':
            errors.append(ValidationError(
                _('Community events are not able to have waiting as status.'),
                code='status_error'
            ))

        if len(errors) > 0:
            raise ValidationError(errors)

    def __str__(self):
        return '{}\'s {}'.format(self.created_under.name_en, self.name_en)


class Lab(Community):
    STATUS = (
        ('R', 'Recruiting'),
        ('C', 'Closed'),
        ('D', 'Disbanded'),
    )

    room = models.CharField(max_length=16, null=True, blank=True)
    founded_date = models.DateField()
    tags = models.CharField(max_length=64)
    status = models.CharField(max_length=1, choices=STATUS, default='R')


# Group 4 - Assets
#   - Announcement
#   - Album
#   - AlbumImage

class Announcement(models.Model):
    text = models.TextField()
    image = models.ImageField(null=True, blank=True)
    created_datetime = models.DateTimeField()
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    creator = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)


class Album(models.Model):
    name = models.CharField(max_length=64)
    created_datetime = models.DateTimeField()
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='created_in')
    community_event = models.ForeignKey(CommunityEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_to')
    creator = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        errors = list()

        try:
            if CommunityEvent.objects.get(pk=self.community.id):
                errors.append(ValidationError(
                    _('Albums are not able to be created under community events.'),
                    code='hierarchy_error'
                ))
        except CommunityEvent.DoesNotExist:
            pass

        try:
            if Event.objects.get(pk=self.community.id) and self.community_event:
                errors.append(ValidationError(
                    _('Albums are not able to be linked to community events if created under an event.'),
                    code='hierarchy_error'
                ))
        except Event.DoesNotExist:
            pass

        if self.community_event and (self.community.id != self.community_event.created_under.id):
            errors.append(ValidationError(
                _('Albums are not able to be linked to community events created under other communities.'),
                code='hierarchy_error'
            ))

        if len(errors) > 0:
            raise ValidationError(errors)


class AlbumImage(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    image = models.ImageField()


class Comment(models.Model):
    text = models.TextField()
    written_by = models.CharField(max_length=128)
    created_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


# Group 5 - Membership
#   - Request
#   - Invitation
#   - Advisory
#   - Membership
#   - CustomMembershipLabel

class Request(models.Model):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Accepted'),
        ('D', 'Declined')
    )

    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='requested_by')
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default='W')
    updated_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_by')


class Invitation(models.Model):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Accepted'),
        ('D', 'Declined')
    )

    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    invitor = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='invitor')
    invitee = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='invitee')
    invited_datetime = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS, default='W')


class Advisory(models.Model):
    advisor = models.ForeignKey(Profile, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        errors = list()

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

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

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
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
