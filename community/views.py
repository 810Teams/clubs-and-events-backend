from datetime import datetime

from rest_framework import generics, status, permissions
from rest_framework.response import Response

from community.models import Club, Event, CommunityEvent, Lab
from community.permissions import IsStudent, IsLecturer, IsPubliclyVisible, IsPresidentOfCommunity, \
    IsVicePresidentOfCommunity, IsDeletableClub
from community.serializers import ClubSerializer, LabSerializer
from membership.models import Membership


class CreateClubView(generics.CreateAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        serializer = ClubSerializer(data=data, many=False)

        if serializer.is_valid():
            club = serializer.save()
            Membership.objects.create(user=user, position=3, community=club, start_date=str(datetime.now().date()))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RetrieveClubView(generics.RetrieveAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [IsPubliclyVisible]

    def get(self, request, *args, **kwargs):
        try:
            club = Club.objects.get(pk=kwargs.get('pk'))
        except Club.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, club)

        serializer = ClubSerializer(club, many=False)

        return Response(serializer.data)


class ListClubView(generics.ListAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not request.user.is_authenticated:
            queryset = queryset.filter(is_publicly_visible=True)

        serializer = ClubSerializer(queryset, many=True)
        return Response(serializer.data)


class UpdateClubView(generics.UpdateAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [IsVicePresidentOfCommunity]

    def put(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        serializer = ClubSerializer(data=data, many=False)

        if serializer.is_valid():
            club = serializer.save()
            self.check_object_permissions(request, club)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DeleteClubView(generics.DestroyAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [IsPresidentOfCommunity, IsDeletableClub]

    def delete(self, request, *args, **kwargs):
        self.check_object_permissions(request, self.get_object())
        self.destroy(request, *args, **kwargs)
        return Response({'success': True}, status=200)
