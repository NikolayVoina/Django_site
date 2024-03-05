"""
URL configuration for marketplace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from marketplace.views import IndexTemplateView
from users.views import EmailVerificationSuccessTemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexTemplateView.as_view(), name="index"),
    path("users/", include("users.urls")),
    path("accounts/", include("allauth.urls")),
    path("accounts/email/verification/success/", EmailVerificationSuccessTemplateView.as_view(), 
         name="account_email_verification_success"),
    path("products/", include("products.urls", namespace="products")),
    path("orders/", include("orders.urls", namespace="orders")),
]

handler404 = "marketplace.views.handler_404"
handler500 = "marketplace.views.handler_500"

urlpatterns.extend(
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
urlpatterns.extend(
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
