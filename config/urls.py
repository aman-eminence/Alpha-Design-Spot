
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

admin.site.site_title = "Alpha Design Spot"
admin.site.site_header = "Alpha Design Spot"
admin.site.index_title = "Site administration"


urlpatterns = [
    path('admin/', admin.site.urls),
    # jwt
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # API Endpoints
    path("api/auth/", include("account.urls"), name="account"),
    path("api/master/", include("master.urls"), name="master"),
    path("api/post/", include("post.urls"), name="master"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:  
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
