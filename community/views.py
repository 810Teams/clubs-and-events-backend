from rest_framework import generics, status, permissions
from rest_framework.response import Response

from community.models import Club, Lab
from community.permissions import IsStudent, IsLecturer
from community.serializers import ClubSerializer, LabSerializer
from membership.models import Membership


class AllClubsView(generics.ListAPIView):
    ''' All clubs view '''
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def get(self, request, *args, **kwargs):
        ''' Get all clubs '''
        queryset = self.get_queryset()

        if not request.user.is_authenticated:
            queryset = queryset.filter(is_publicly_visible=True)

        serializer = ClubSerializer(queryset, many=True)
        return Response(serializer.data)


class CreateClubView(generics.CreateAPIView):
    ''' Own clubs view '''
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def post(self, request, *args, **kwargs):
        ''' Create a club '''
        data = request.data

        serializer = ClubSerializer(data=data, many=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ClubView(generics.RetrieveAPIView, generics.UpdateAPIView):
    ''' Club view '''
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def get(self, request, *args, **kwargs):
        ''' Get club '''
        user = request.user

        try:
            club = Club.objects.get(pk=kwargs.get('pk'))
        except Club.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not club.is_publicly_visible and not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = ClubSerializer(club, many=False)

        return Response(serializer.data)


    def patch(self, request, *args, **kwargs):
        ''' Update the club '''
        data = request.data
        user = request.user

        try:
            membership = Membership.objects.get(user=user.id, community=kwargs.get('pk'), end_date=None)

            if membership.position not in [2, 3]:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Membership.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = ClubSerializer(data=data, many=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
