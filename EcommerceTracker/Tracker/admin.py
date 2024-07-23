from django.contrib import admin
from .models import TrackData

@admin.register(TrackData)
class TrackDataAdmin(admin.ModelAdmin):
    list_display = ( 'Id','Name_Url', 'Title', 'Item_Url', 'Item_Price', 'Item_Image_url', 'Expected_Price', 'Email', 'last_updated')
    search_fields = ('Name_Url', 'Title', 'Email')
    list_filter = ('last_updated',)
