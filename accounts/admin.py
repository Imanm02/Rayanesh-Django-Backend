from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext, gettext_lazy as _

from import_export.admin import ImportExportModelAdmin

from .resources import ProfileResource
from .models import User, Profile, GoogleLogin


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    list_display = ('username', 'name')
    list_filter = ('username', 'name', 'university_degree')

    search_fields = ('username', 'name', 'email',)

    resource_class = ProfileResource

@admin.register(GoogleLogin)
class GoogleLoginAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_signup')
    list_display_links = ('id', 'email')
    search_fields = ('email',)


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    pass


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    pass
