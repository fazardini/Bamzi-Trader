from django.contrib import admin

from bamzi.models import Industry, Share, UserShare, ShareConvention

class ShareAdmin(admin.ModelAdmin):
    list_display = ('symbol_name', 'company_name')
    list_display_links = ('symbol_name', 'company_name')

admin.site.register(Industry)
admin.site.register(Share, ShareAdmin)
admin.site.register(UserShare)
admin.site.register(ShareConvention)