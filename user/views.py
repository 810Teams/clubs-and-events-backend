from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters, status, generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.settings import api_settings

from community.models import Club, CommunityEvent, Community
from core.utils import filter_queryset
from membership.models import Membership, Invitation, Request
from user.models import EmailPreference, StudentCommitteeAuthority
from user.permissions import IsProfileOwner, IsEmailPreferenceOwner
from user.serializers import UserSerializer, LimitedUserSerializer, EmailPreferenceSerializer
from user.serializers import StudentCommitteeAuthoritySerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    http_method_names = ('get', 'put', 'patch', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'name', 'nickname')

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH'):
            return (permissions.IsAuthenticated(), IsProfileOwner())
        return tuple()

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return UserSerializer
        return LimitedUserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if self.request.user.is_authenticated:
            queryset = filter_queryset(queryset, request, target_param='is_lecturer', is_foreign_key=False)
            queryset = filter_queryset(queryset, request, target_param='is_active', is_foreign_key=False)
            queryset = filter_queryset(queryset, request, target_param='is_staff', is_foreign_key=False)
            queryset = filter_queryset(queryset, request, target_param='is_superuser', is_foreign_key=False)

            # URL Argument: is_applicable_for
            try:
                community_id = request.query_params.get('is_applicable_for')

                if community_id is not None:
                    community_id = int(community_id)
                    excluded_ids = list()

                    # Case 1: Exclude lecturers if the community is club
                    try:
                        Club.objects.get(pk=community_id)
                        excluded_ids += [i.id for i in get_user_model().objects.all() if i.is_lecturer]
                    except Club.DoesNotExist:
                        pass

                    # Case 2: Community is community event and doesn't allow outside participators
                    try:
                        community_event = CommunityEvent.objects.get(pk=community_id)
                        base_community = Community.objects.get(pk=community_event.created_under.id)
                        base_membership_ids = [i.id for i in Membership.objects.filter(community_id=base_community.id)]
                        excluded_ids += [i.id for i in get_user_model().objects.all() if i not in base_membership_ids]
                    except CommunityEvent.DoesNotExist:
                        pass

                    # Case 3: Already a member
                    excluded_ids += [i.id for i in Membership.objects.filter(
                        community_id=community_id,status__in=('A', 'R')
                    )]

                    # Case 4: Already has pending request
                    excluded_ids += [i.id for i in Invitation.objects.filter(community_id=community_id, status='W')]

                    # Case 5: Already has pending invitation
                    excluded_ids += [i.id for i in Request.objects.filter(community_id=community_id, status='W')]

                    # Excluding Process
                    queryset = queryset.exclude(pk__in=excluded_ids)
            except ValueError:
                queryset = None

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class MyUserView(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        user = self.get_queryset().get(pk=request.user.id)
        serializer = self.get_serializer(user, many=False)

        return Response(serializer.data)


class LoginAPIView(ObtainAuthToken):
   renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class EmailPreferenceViewSet(viewsets.ModelViewSet):
    queryset = EmailPreference.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsEmailPreferenceOwner)
    serializer_class = EmailPreferenceSerializer
    http_method_names = ('get', 'put', 'patch', 'head', 'options')

    def list(self, request, *args, **kwargs):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN
        )


class MyEmailPreferenceView(generics.ListAPIView):
    queryset = EmailPreference.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailPreferenceSerializer

    def list(self, request, *args, **kwargs):
        email_preference = self.get_queryset().get(user_id=request.user.id)
        serializer = self.get_serializer(email_preference, many=False)

        return Response(serializer.data)


class StudentCommitteeAuthorityViewSet(viewsets.ModelViewSet):
    queryset = StudentCommitteeAuthority.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = StudentCommitteeAuthoritySerializer
    http_method_names = ('get', 'head', 'options')


class MyStudentCommitteeAuthorityView(generics.ListAPIView):
    queryset = StudentCommitteeAuthority.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = StudentCommitteeAuthoritySerializer

    def list(self, request, *args, **kwargs):
        try:
            student_committee_authority = self.get_queryset().get(user_id=request.user.id)
            serializer = self.get_serializer(student_committee_authority, many=False)

            return Response(serializer.data)
        except StudentCommitteeAuthority.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
