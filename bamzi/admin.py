from django.contrib import admin
from bamzi.models import Industry, Share, UserShare, ShareConvention
from jalali_date.admin import ModelAdminJalaliMixin, StackedInlineJalaliMixin, TabularInlineJalaliMixin	
from jalali_date import datetime2jalali


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ('symbol_name', 'company_name')
    list_display_links = ('symbol_name', 'company_name')


@admin.register(UserShare)
class UserShareAdmin(admin.ModelAdmin):
    list_display = ('user', 'share')
    list_display_links = ('user', 'share')


@admin.register(ShareConvention)
class FirstModelAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):

	def get_created_jalali(self, obj):
		return datetime2jalali(obj.convention_date).strftime('%y/%m/%d _ %H:%M:%S')
	
	get_created_jalali.short_description = 'تاریخ مجمع'
	get_created_jalali.admin_order_field = 'convention_date'

admin.site.register(Industry)