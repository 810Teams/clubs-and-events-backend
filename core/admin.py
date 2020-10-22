'''
    Core Application Django Admin
    core/admin.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib import admin
from django.contrib.auth.models import Permission


admin.site.register(Permission)
