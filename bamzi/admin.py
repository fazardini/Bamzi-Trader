from django.contrib import admin

from bamzi.models import Industry, Share, UserShare, ShareConvention

class ShareAdmin(admin.ModelAdmin):
    list_display = ('symbol_name', 'company_name')
    list_display_links = ('symbol_name', 'company_name')

class UserShareAdmin(admin.ModelAdmin):
    list_display = ('user', 'share')
    list_display_links = ('user', 'share')

admin.site.register(Industry)
admin.site.register(Share, ShareAdmin)
admin.site.register(UserShare, UserShareAdmin)
admin.site.register(ShareConvention)