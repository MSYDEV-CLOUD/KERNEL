from django.contrib import admin
from .models import IFTARate

@admin.register(IFTARate)
class IFTARateAdmin(admin.ModelAdmin):
    list_display = ('state_province', 'us_diesel_rate', 'ca_diesel_rate', 'us_surcharge', 'ca_surcharge', 'date_scraped')
    search_fields = ('state_province',)

