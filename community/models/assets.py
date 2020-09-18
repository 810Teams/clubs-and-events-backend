from django.db import models
from community.models.community import Community
from community.models.community import CommunityEvent
from community.models.profile import Profile

class Request(models.Model):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Accepted'),
        ('D', 'Declined')
    )

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, default='W')

class Announcement(models.Model):
    text = models.TextField()
    image = models.ImageField()
    created_datetime = models.DateTimeField()
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    creator = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)

class Album(models.Model):
    name = models.CharField(max_length=64)
    created_datetime = models.DateTimeField()
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    community_event = models.ForeignKey(CommunityEvent, on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)

class AlbumImage(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    image = models.ImageField()

class Invitation(models.Model):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Accepted'),
        ('D', 'Declined')
    )

    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    invitor = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    invitee = models.ForeignKey(Profile, on_delete=models.CASCADE)
    invited_datetime = models.DateTimeField()
    status = models.CharField(choices=STATUS, default='W')

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
    ended_reason = models.CharField(choices=ENDED_REASON)

class CustomMembershipLabel(models.Model):
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE)
    custom_label = models.CharField(max_length=32)
