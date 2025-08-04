from django.contrib import admin
from .models import OS, Estado



@admin.register(OS)
class OSAdmin(admin.ModelAdmin):
    list_display = ('name','description','create_at')

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('name','color')