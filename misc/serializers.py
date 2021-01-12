'''
    Miscellaneous Application Serializers
    misc/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import serializers

from misc.models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    ''' Frequently asked question (FAQ) serializer '''
    class Meta:
        ''' Meta '''
        model = FAQ
        exclude = ('created_by', 'updated_by')
