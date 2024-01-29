import os

from django.contrib import admin
from django.utils.html import format_html
from dotenv import load_dotenv

from .models import ClassEvaluation, SingleEvaluation, Item, NWFGEvaluation, NWFGEvaluationPart, NWFGSingleEvaluation, NWFGItem, NWFGEvaluationAcronym

ENV = load_dotenv('../.env')
BASE_URL = os.getenv('WEBSITE_URL')

admin.site.index_title = "FALKO-PV Admin"
admin.site.site_header = "FALKO-PV Admin"
admin.site.site_title = "FALKO-PV Admin"


@admin.register(ClassEvaluation)
class ClassEvaluationAdmin(admin.ModelAdmin):

    @admin.display(description='Status URL')
    def get_status_url(self, obj):
        url = f"evaluation/{obj.class_evaluation_id}/status/{obj.status_url_token}"
        return format_html(f"<a href='{BASE_URL}{url}', target='_blank'>Status Link</a>")

    @admin.display(description='Started by')
    def get_started(self, obj):
        return len(SingleEvaluation.objects.filter(class_evaluation_id=obj.class_evaluation_id))

    @admin.display(description='Completed by')
    def get_completed(self, obj):
        return len(SingleEvaluation.objects.filter(class_evaluation_id=obj.class_evaluation_id).filter(completed=True))

    date_hierarchy = 'creation_timestamp'

    ordering = ('-creation_timestamp',)

    list_display = (
        'class_evaluation_id',
        'context_of_use',
        'subject',
        'creation_timestamp',
        'email',
        'get_started',
        'get_completed',
        'completed',
        'deleted',
        'get_status_url',
    )

    list_filter = ('subject', 'completed', 'deleted', 'context_of_use')

    search_fields = ['email', 'teacher_name']

    search_help_text = 'Nach E-Mail Adresse oder Lehrkraft Name suchen.'

    empty_value_display = '--'

    exclude = ('start_evaluation_immediately', 'status_url_token')

    fieldsets = (
        ('Persönliche Angaben', {
            'fields': (('email', 'teacher_name'), 'subject'),
        }),
        ('Einstellungen Datum u. Zeit', {
            'fields': ('evaluation_start', 'evaluation_end', 'evaluation_stopped_timestamp'),
        }),
        ('Sonstige Einstellungen', {
            'fields': (('email_sent_evaluation_end', 'completed', 'deleted'),)
        })
    )


@admin.register(SingleEvaluation)
class SingleEvaluationAdmin(admin.ModelAdmin):
    list_display = ('single_evaluation_id', 'completed', 'class_evaluation')

    search_fields = ('class_evaluation',)

    search_help_text = "Nach einer bestimmten ClassEvaluation suchen."


admin.site.register(NWFGEvaluation)
admin.site.register(NWFGEvaluationPart)
admin.site.register(Item)
admin.site.register(NWFGSingleEvaluation)
admin.site.register(NWFGItem)
admin.site.register(NWFGEvaluationAcronym)
