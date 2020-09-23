from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from community.models import Club
from community.serializers import ClubSerializer
from membership.models import Membership
from user.models import User


class OwnClubsView(generics.ListAPIView, generics.CreateAPIView):
    ''' Club view '''
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        memberships = Membership.objects.filter(user=request.user.id)
        queryset = self.get_queryset().filter(pk__in=[i.community for i in memberships])
        serializer = ClubSerializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        if User.objects.get(user=user.id).is_lecturer:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            serializer = ClubSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

