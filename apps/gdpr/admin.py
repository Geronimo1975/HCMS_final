from django.contrib import admin
from .models import LegalDocumentVersion

def fill_with_boilerplate(modeladmin, request, queryset):
    for obj in queryset:
        obj.fill_with_template()
        obj.save()
fill_with_boilerplate.short_description = "Fill selected with boilerplate"

@admin.register(LegalDocumentVersion)
class LegalDocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('doc_type', 'language', 'version', 'published_at')
    list_filter = ('doc_type', 'language')
    search_fields = ('content', 'version')
    readonly_fields = ('published_at',)
    actions = [fill_with_boilerplate]
