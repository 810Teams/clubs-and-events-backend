from datetime import datetime

from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response

from community.models import Club, Event, CommunityEvent, Lab
from community.permissions import IsStudent, IsLecturer, IsPubliclyVisible, IsPresidentOfCommunity, \
    IsVicePresidentOfCommunity, IsDeletableClub
from community.serializers import ClubSerializer, LabSerializer
from membership.models import Membership


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsPubliclyVisible(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(), IsStudent())
        elif self.request.method in ['PUT', 'PATCH']:
            return (IsVicePresidentOfCommunity(),)
        elif self.request.method == 'DELETE':
            return (IsPresidentOfCommunity(), IsDeletableClub())
        return tuple()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not request.user.is_authenticated:
            queryset = queryset.filter(is_publicly_visible=True, is_official=True)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            club = Club.objects.get(pk=kwargs.get('pk'))
        except Club.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, club)

        serializer = self.get_serializer(club, many=False)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        serializer = self.get_serializer(data=data, many=False)

        if serializer.is_valid():
            club = serializer.save()
            Membership.objects.create(user=user, position=3, community=club, start_date=str(datetime.now().date()))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data = request.data

        serializer = self.get_serializer(data=data, many=False)

        if serializer.is_valid():
            club = serializer.save()
            self.check_object_permissions(request, club)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        self.check_object_permissions(request, self.get_object())
        self.destroy(request, *args, **kwargs)
        return Response({'success': True}, status=200)
