from django.contrib import admin

from .models import Server
from .forms import ServerForm


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    form = ServerForm
