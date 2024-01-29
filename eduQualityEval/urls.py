from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', include('evaluation_tool.urls')),
    path('admin/', admin.site.urls),
    path('captcha', include('captcha.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "evaluation_tool.views.page_not_found_view_404"
