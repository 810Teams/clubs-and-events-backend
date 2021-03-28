'''
    Core Application Views
    core/views.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from clubs_and_events.settings import LANGUAGE_CODE, TIME_ZONE, USE_TZ, ENABLE_LDAP
from clubs_and_events.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_USE_TLS
from clubs_and_events.settings import EMAIL_DOMAIN_NAME, EMAIL_NOTIFICATIONS, SEND_IMAGES_AS_ATTACHMENTS
from clubs_and_events.settings import DO_IMAGE_DOWNSCALING, MAX_ANNOUNCEMENT_IMAGE_DIMENSION, MAX_ALBUM_IMAGE_DIMENSION
from clubs_and_events.settings import MAX_COMMUNITY_LOGO_DIMENSION, MAX_COMMUNITY_BANNER_DIMENSION
from clubs_and_events.settings import MAX_PROFILE_PICTURE_DIMENSION
from clubs_and_events.settings import CLUB_VALID_MONTH, CLUB_VALID_DAY,CLUB_ADVANCED_RENEWAL
from clubs_and_events.settings import STUDENT_COMMITTEE_ADVISOR_NAME, STUDENT_COMMITTEE_PRESIDENT_NAME
from clubs_and_events.settings import COMMENT_LIMIT_PER_INTERVAL, COMMENT_INTERVAL_TIME
from clubs_and_events.settings import VOTE_LIMIT_PER_EVENT, NLP_EN_MODEL

import datetime

@api_view(['GET'])
def get_datetime(request):
    ''' Get date and time '''
    return Response({
        'datetime_now': datetime.datetime.now(),
        'timezone_now': timezone.now()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_settings(request):
    ''' Get backend settings '''
    return Response({
        'internationalization': {
            'language_code': LANGUAGE_CODE,
            'timezone': TIME_ZONE,
            'use_timezone': USE_TZ
        },
        'ldap': {
            'enable_ldap': ENABLE_LDAP
        },
        'email': {
            'email_host': EMAIL_HOST,
            'email_port': EMAIL_PORT,
            'email_host_user': EMAIL_HOST_USER,
            'email_use_tls': EMAIL_USE_TLS,
        },
        'notification': {
            'email_domain_name': EMAIL_DOMAIN_NAME,
            'email_notification': EMAIL_NOTIFICATIONS,
            'send_images_as_attachments': SEND_IMAGES_AS_ATTACHMENTS
        },
        'storage': {
            'do_image_downscaling': DO_IMAGE_DOWNSCALING,
            'max_announcement_image_dimension': list(MAX_ANNOUNCEMENT_IMAGE_DIMENSION),
            'max_album_image_dimension': list(MAX_ALBUM_IMAGE_DIMENSION),
            'max_community_logo_image_dimension': list(MAX_COMMUNITY_LOGO_DIMENSION),
            'max_community_banner_image_dimension': list(MAX_COMMUNITY_BANNER_DIMENSION),
            'max_profile_picture_image_dimension': list(MAX_PROFILE_PICTURE_DIMENSION)
        },
        'club': {
            'club_valid_month': CLUB_VALID_MONTH,
            'club_valid_day': CLUB_VALID_DAY,
            'club_advanced_renewal': CLUB_ADVANCED_RENEWAL.days,
            'student_committee_advisor_name': STUDENT_COMMITTEE_ADVISOR_NAME,
            'student_committee_president_name': STUDENT_COMMITTEE_PRESIDENT_NAME
        },
        'comment': {
            'comment_limit_per_interval': COMMENT_LIMIT_PER_INTERVAL,
            'comment_interval_time': COMMENT_INTERVAL_TIME.seconds // 60
        },
        'vote': {
            'vote_limit_per_event': VOTE_LIMIT_PER_EVENT
        },
        'nlp': {
            'nlp_en_model': NLP_EN_MODEL
        }
    }, status=status.HTTP_200_OK)
