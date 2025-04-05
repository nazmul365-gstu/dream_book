from django.contrib import admin
from django.utils.html import format_html
from .models import BookType, Book, Review

class BookAdmin(admin.ModelAdmin):
    fields = ('title', 'author', 'book_type', 'description', 'price', 'published_date', 'is_free', 'image_url', 'download_link', 'added_by')
    list_display = ('title', 'author', 'book_type', 'is_free', 'image_url_display', 'download_link_display', 'added_by')
    list_filter = ('is_free', 'book_type')
    search_fields = ('title', 'author')

    def image_url_display(self, obj):
        if obj.image_url:
            return format_html('<a href="{}" target="_blank">View Image</a>', obj.image_url)
        return "No URL"
    image_url_display.short_description = 'Image URL'

    def download_link_display(self, obj):
        if obj.download_link:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.download_link)
        return "No URL"
    download_link_display.short_description = 'Download URL'


# মডেল রেজিস্টার করা
admin.site.register(BookType)
admin.site.register(Book, BookAdmin)
admin.site.register(Review)