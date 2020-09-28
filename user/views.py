from rest_framework import viewsets, filters, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.settings import api_settings

from core.utils import filter_queryset
from user.models import User, EmailPreference
from user.permissions import IsProfileOwner
from user.serializers import UserSerializer, LimitedUserSerializer, EmailPreferenceSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
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
        queryset = self.get_queryset()

        if self.request.user.is_authenticated:
            queryset = filter_queryset(queryset, request, target_param='is_active', is_foreign_key=False)
            queryset = filter_queryset(queryset, request, target_param='is_staff', is_foreign_key=False)
            queryset = filter_queryset(queryset, request, target_param='is_superuser', is_foreign_key=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class LoginAPIView(ObtainAuthToken):
   renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class EmailPreferenceViewSet(viewsets.ModelViewSet):
    queryset = EmailPreference.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsProfileOwner)
    serializer_class = EmailPreferenceSerializer
    http_method_names = ('get', 'put', 'patch', 'head', 'options')

    def list(self, request, *args, **kwargs):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN
        )
