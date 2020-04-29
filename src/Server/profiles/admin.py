from django.contrib import admin

# Register your models here.
from .models import Profile, SocialLink, Settings


class SettingsInline(admin.TabularInline):
    model = Settings


class SocialLinksInline(admin.TabularInline):
    model = SocialLink


class ProfileAdmin(admin.ModelAdmin):
    inlines = [SocialLinksInline, SettingsInline]

    class Meta:
        model = Profile


admin.site.register(Profile, ProfileAdmin)
