'''
    User Application Views
    user/views.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from crum import get_current_request
from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters, status, generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.settings import api_settings

from community.models import Club, CommunityEvent, Community, Lab
from core.filters import filter_queryset
from core.utils import has_instance
from membership.models import Membership, Invitation, Request
from user.models import EmailPreference, StudentCommitteeAuthority
from user.permissions import IsProfileOwner, IsEmailPreferenceOwner, IsLecturerObject, IsStudentObject
from user.serializers import UserSerializer, LimitedUserSerializer, EmailPreferenceSerializer
from user.serializers import StudentCommitteeAuthoritySerializer


class UserViewSet(viewsets.ModelViewSet):
    ''' User view set '''
    queryset = get_user_model().objects.all()
    http_method_names = ('get', 'put', 'patch', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'name', 'nickname')

    def get_permissions(self):
        ''' Get permissions '''
        if self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsProfileOwner())
        return tuple()

    def get_serializer_class(self):
        ''' Get serializer class '''
        if self.request.user.is_authenticated:
            return UserSerializer
        return LimitedUserSerializer

    def list(self, request, *args, **kwargs):
        ''' List users '''
        queryset = self.filter_queryset(self.get_queryset())

        if self.request.user.is_authenticated:
            queryset = filter_queryset(queryset, request, target_param='user_group', is_foreign_key=False)
            queryset = filter_queryset(queryset, request, target_param='is_active', is_foreign_key=False)
            queryset = filter_queryset(queryset, request, target_param='is_staff', is_foreign_key=False)
            queryset = filter_queryset(queryset, request, target_param='is_superuser', is_foreign_key=False)

            # URL Argument: is_applicable_for
            try:
                community_id = request.query_params.get('is_applicable_for')

                if community_id is not None:
                    community = Community.objects.get(pk=int(community_id))
                    excluded_ids = list()

                    # Case 1: Exclude non-students if the community is club
                    if has_instance(community, Club):
                        excluded_ids += [
                            i.id for i in get_user_model().objects.all() if not IsStudentObject().has_object_permission(
                                get_current_request(), None, i
                            )
                        ]

                    # Case 2: Exclude non-students and non-lecturers if the community is lab
                    elif has_instance(community, Lab):
                        excluded_ids += [
                            i.id for i in get_user_model().objects.all() if not IsStudentObject().has_object_permission(
                                get_current_request(), None, i
                            ) and not IsLecturerObject().has_object_permission(
                                get_current_request(), None, i
                            )
                        ]

                    # Case 3: Community is community event and doesn't allow outside participators
                    elif has_instance(community, CommunityEvent):
                        community_event = CommunityEvent.objects.get(pk=community.id)
                        if not community_event.allows_outside_participators:
                            base_community = Community.objects.get(pk=community_event.created_under.id)
                            base_membership_ids = [i.id for i in Membership.objects.filter(
                                community_id=base_community.id, status__in=('A', 'R')
                            )]
                            excluded_ids += [i.id for i in get_user_model().objects.exclude(pk__in=base_membership_ids)]

                    # Case 4: Already a member
                    excluded_ids += [i.user.id for i in Membership.objects.filter(
                        community_id=community.id, status__in=('A', 'R')
                    )]

                    # Case 5: Already has pending invitation
                    excluded_ids += [i.invitee.id for i in Invitation.objects.filter(
                        community_id=community.id, status='W'
                    )]

                    # Case 6: Already has pending request
                    excluded_ids += [i.user.id for i in Request.objects.filter(community_id=community_id, status='W')]

                    # Excluding Process
                    queryset = queryset.exclude(pk__in=excluded_ids)
            except (ValueError, Community.DoesNotExist):
                queryset = None

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class MyUserView(generics.ListAPIView):
    ''' My user view '''
    queryset = get_user_model().objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        ''' Retrieve own user '''
        user = self.get_queryset().get(pk=request.user.id)
        serializer = self.get_serializer(user, many=False)

        return Response(serializer.data)


class LoginAPIView(ObtainAuthToken):
    ''' Login view '''
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class EmailPreferenceViewSet(viewsets.ModelViewSet):
    ''' Email preference view set '''
    queryset = EmailPreference.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsEmailPreferenceOwner)
    serializer_class = EmailPreferenceSerializer
    http_method_names = ('get', 'put', 'patch', 'head', 'options')

    def list(self, request, *args, **kwargs):
        ''' List email preferences '''
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN
        )


class MyEmailPreferenceView(generics.ListAPIView):
    ''' My email preference view '''
    queryset = EmailPreference.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailPreferenceSerializer

    def list(self, request, *args, **kwargs):
        ''' Retrieve own email preference '''
        email_preference = self.get_queryset().get(user_id=request.user.id)
        serializer = self.get_serializer(email_preference, many=False)

        return Response(serializer.data)


class StudentCommitteeAuthorityViewSet(viewsets.ModelViewSet):
    ''' Student committee authority view set '''
    queryset = StudentCommitteeAuthority.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = StudentCommitteeAuthoritySerializer
    http_method_names = ('get', 'head', 'options')


class MyStudentCommitteeAuthorityView(generics.ListAPIView):
    ''' My student committee authority view '''
    queryset = StudentCommitteeAuthority.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = StudentCommitteeAuthoritySerializer

    def list(self, request, *args, **kwargs):
        ''' Retrieve own student committee authority '''
        try:
            student_committee_authority = self.get_queryset().get(user_id=request.user.id)
            serializer = self.get_serializer(student_committee_authority, many=False)

            return Response(serializer.data)
        except StudentCommitteeAuthority.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
