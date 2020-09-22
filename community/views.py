import json

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import condition
from django.core import serializers

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from community.models import Club
from community.serializers import ClubSerializer

@api_view(['GET'])
def api_overview(request):
    response = {''}

    return Response(response)

@api_view(['GET'])
def get_clubs(request):
    response = {}

    clubs = Club.objects.all()
    serializer = ClubSerializer(clubs, many=True)

    return Response(serializer.data)

