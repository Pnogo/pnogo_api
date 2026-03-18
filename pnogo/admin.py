from django.contrib import admin

from .models import Cndr, Picture


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "description", "cndr", "points", "sent", "daily_date")
    list_filter = ("cndr", "daily_date")
    search_fields = ("file", "description")
    raw_id_fields = ("cndr",)


@admin.register(Cndr)
class CndrAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
