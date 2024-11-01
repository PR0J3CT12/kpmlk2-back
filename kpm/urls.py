from django.contrib import admin
from django.urls import path, include
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view
from django.conf import settings
from django.conf.urls.static import static

schema_view = swagger_get_schema_view(
    openapi.Info(
        title="KPM API",
        default_version='2.0.0',
        description="API documentation of KPM-LK",
    ),
    public=True,
    url=''
)

urlpatterns = [
    path('api/user/', include('users.urls')),
    path('api/group/', include('groups.urls')),
    path('api/grade/', include('grades.urls')),
    path('api/mana/', include('grades.urls_mana')),
    path('api/theme/', include('themes.urls')),
    path('api/work/', include('works.urls')),
    path('api/classwork/', include('works.urls_classworks')),
    path('api/homework/', include('works.urls_homeworks')),
    path('api/individual-work/', include('works.urls_individual_works')),
    path('api/message/', include('messages.urls')),
    path('api/stat/', include('stats.urls')),
    path('api/rating/', include('ratings.urls')),
    path('api/notification/', include('notifications.urls')),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('api/docs', schema_view.with_ui('swagger', cache_timeout=0), name="swagger-schema")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
