from django.contrib import admin
from bamzi.models import Industry, Share, UserShare, ShareConvention, PrecedenceShare
from bamzi.models import UserPrecedenceShare, ConventionBenefit, UserConventionBenefit
from jalali_date.admin import ModelAdminJalaliMixin	
from jalali_date import datetime2jalali


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ('symbol_name', 'company_name')
    list_display_links = ('symbol_name', 'company_name')
    search_fields = ('symbol_name', 'company_name')


@admin.register(UserShare)
class UserShareAdmin(admin.ModelAdmin):
    list_display = ('user', 'share')
    list_display_links = ('user', 'share')


@admin.register(ShareConvention)
class ShareConventionAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):

    def get_convention_jalali(self, obj):
        return datetime2jalali(obj.convention_date).strftime('%y/%m/%d _ %H:%M:%S')
    
    get_convention_jalali.short_description = 'تاریخ مجمع'
    get_convention_jalali.admin_order_field = 'convention_date'


@admin.register(PrecedenceShare)
class PrecedenceShareAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):

    def get_from_jalali(self, obj):
        return datetime2jalali(obj.from_date).strftime('%y/%m/%d _ %H:%M:%S')

    def get_to_jalali(self, obj):
        return datetime2jalali(obj.to_date).strftime('%y/%m/%d _ %H:%M:%S')

    get_from_jalali.short_description = 'از تاریخ'
    get_from_jalali.admin_order_field = 'from_date'
    get_to_jalali.short_description = 'تا تاریخ'
    get_to_jalali.admin_order_field = 'to_date'
    search_fields = ('share__symbol_name', )


@admin.register(ConventionBenefit)
class ConventionBenefitAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):

    def get_from_jalali(self, obj):
        return datetime2jalali(obj.from_date).strftime('%y/%m/%d _ %H:%M:%S')

    def get_to_jalali(self, obj):
        return datetime2jalali(obj.to_date).strftime('%y/%m/%d _ %H:%M:%S')

    get_from_jalali.short_description = 'از تاریخ'
    get_from_jalali.admin_order_field = 'from_date'
    get_to_jalali.short_description = 'تا تاریخ'
    get_to_jalali.admin_order_field = 'to_date'

    search_fields = ('share__symbol_name', )


admin.site.register(Industry)
admin.site.register(UserPrecedenceShare)
admin.site.register(UserConventionBenefit)