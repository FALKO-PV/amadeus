from django.urls import path
from . import views
from . import student_auth_views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from .api import api
from . import views_docs

urlpatterns = [
    path('', views.get_start_page, name="start_page"),
    path('informationen-durchfuehrung', views_docs.get_tutorial_page, name="tutorial_page"),
    path('ueber-modellierung', views_docs.get_modelling_info_page, name="modelling_info_page"),
    path('ueber-evaluierung', views_docs.get_evaluation_info_page, name="evaluation_info_page"),
    path('faq', views_docs.get_faq_page, name="faq_page"),
    path('app', views.get_create_evaluation_page, name="create_evaluation_page"),
    path('api/create-evaluation/<nwfg_code>', api.create_evaluation_api, name="create_evaluation_api"),
    path('datenschutzhinweise', views.get_datenschutzhinweise_page, name="datenschutzhinweise"),
    path('impressum', views.get_impressum_page, name="impressum"),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', TemplateView.as_view(template_name="sitemap.xml", content_type="text/plain")),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('icons/favicon.ico'))),
    path('evaluation/<str:evaluation_id>/share', views.get_share_page, name="share-page"),
    path('evaluation/<str:evaluation_id>', views.get_start_evaluation, name="start-evaluation-page"),
    path('evaluation/<str:evaluation_id>/auth', student_auth_views.get_auth_student_page, name="auth-student-page"),
    path('evaluation/<str:evaluation_id>/new-auth', student_auth_views.get_new_auth_student_page, name="new-auth-student-page"),
    path('evaluation/<str:evaluation_id>/evaluate/<str:single_evaluation_id>', views.get_evaluation_form_page, name="evaluation-form-page"),
    path('evaluation/<str:evaluation_id>/evaluate/<str:single_evaluation_id>/complete', views.get_evaluation_form_page_submit, name="evaluation-form-page-submit"),
    path('evaluation/<str:evaluation_id>/status/<str:status_code>', views.get_status_page, name="status-page"),
    path('evaluation/<str:evaluation_id>/status/<str:status_code>/download_excel', views.download_csv, name="download_excel"),
    path('evaluation/<str:evaluation_id>/status/<str:status_code>/get_pdf', views.get_evaluation_pdf, name="get_pdf"),
]