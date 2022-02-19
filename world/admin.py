from django.contrib import admin

from world.models import Attrib, Concept


class AttribInline(admin.TabularInline):
    model = Attrib
    extra = 0
    fields = ('name', 'datatype', 'metadata')
    ordering = ('time_added', )
    show_full_result_count = True
    show_change_link = True


class ConceptAdmin(admin.ModelAdmin):
    inlines = [AttribInline, ]
    list_display = ('name', 'hint', 'time_updated', 'time_added')
    ordering = ('-time_added', )


admin.site.register(Concept, ConceptAdmin)
