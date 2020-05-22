from django.contrib import admin

from bamzi.models import Industry, Share, UserShare

admin.site.register(Industry)
admin.site.register(Share)
admin.site.register(UserShare)