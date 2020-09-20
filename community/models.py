from django.db import models

# Group 1 - User
#   - EmailPreferences
#   - Profile
#   - StudentCommitteeAuthority

class EmailPreferences(models.Model):
    receive_own_club = models.BooleanField(default=True)
    receive_own_event = models.BooleanField(default=True)
    receive_own_lab = models.BooleanField(default=True)
    receive_other_events = models.BooleanField(default=True)


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
    email_preferences = models.OneToOneField(EmailPreferences, on_delete=models.PROTECT)


class StudentCommitteeAuthority(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()


# Group 2 - Types
#   - ClubType
#   - EventType
#   - EventSeries

class ClubType(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)


class EventType(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)


class EventSeries(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)


# Group 3 - Community
#   - Community
#   - Club
#   - Event
#   - CommunityEvent
#   - Lab

class Community(models.Model):
    name_th = models.CharField(max_length=64)
    name_en = models.CharField(max_length=64)
    url_id = models.CharField(max_length=16, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)
    banner = models.ImageField(null=True, blank=True)
    is_publicly_visible = models.BooleanField(default=False)


class Club(Community):
    STATUS = (
        ('R', 'Recruiting'),
        ('C', 'Closed'),
        ('D', 'Disbanded'),
    )

    club_type = models.ForeignKey(ClubType, on_delete=models.SET_NULL, null=True)
    room = models.CharField(max_length=32, null=True, blank=True)
    founded_date = models.DateField()
    is_official = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=STATUS, default='R')


class Event(Community):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Approved'),
        ('C', 'Cancelled'),
    )

    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True)
    event_series = models.ForeignKey(EventSeries, on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=256)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=1, choices=STATUS, default='W')


class CommunityEvent(Event):
    created_under = models.ForeignKey(Community, on_delete=models.PROTECT)
    allows_outside_participators = models.BooleanField(default=False)


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
    image = models.ImageField()
    created_datetime = models.DateTimeField()
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    creator = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)


class Album(models.Model):
    name = models.CharField(max_length=64)
    created_datetime = models.DateTimeField()
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='created_in')
    community_event = models.ForeignKey(CommunityEvent, on_delete=models.SET_NULL, null=True, related_name='linked_to')
    creator = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)


class AlbumImage(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    image = models.ImageField()


class Comment(models.Model):
    text = models.CharField(max_length=512)
    written_by = models.CharField(max_length=128)
    created_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
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

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default='W')


class Invitation(models.Model):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Accepted'),
        ('D', 'Declined')
    )

    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    invitor = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='invitor')
    invitee = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='invitee')
    invited_datetime = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS, default='W')


class Advisory(models.Model):
    advisor = models.ForeignKey(Profile, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()


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
    ended_reason = models.CharField(max_length=1, choices=ENDED_REASON)


class CustomMembershipLabel(models.Model):
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE)
    custom_label = models.CharField(max_length=32)
