from django.contrib import admin

from .models import Server, Folder
from .forms import ServerForm


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    form = ServerForm


admin.site.register(Folder)
