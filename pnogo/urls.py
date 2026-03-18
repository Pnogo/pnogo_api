from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

from . import views


def health(request):
    return HttpResponse("OK")


api_urlpatterns = [
    # Pictures CRUD
    path("pictures/", views.PictureListView.as_view(), name="picture-list"),
    path("pictures/upload/", views.PictureUploadView.as_view(), name="picture-upload"),
    path("pictures/count/", views.PictureCountView.as_view(), name="picture-count"),
    path("pictures/random/", views.PictureRandomView.as_view(), name="picture-random"),
    path("pictures/daily/", views.PictureDailyView.as_view(), name="picture-daily"),
    path("pictures/<int:pk>/", views.PictureDetailView.as_view(), name="picture-detail"),
    path("pictures/<int:pk>/image/", views.PictureImageView.as_view(), name="picture-image"),
    path("pictures/<int:pk>/stretched/", views.PictureStretchedView.as_view(), name="picture-stretched"),
    path("pictures/<int:pk>/bitmap/", views.PictureBitmapView.as_view(), name="picture-bitmap"),
    path("pictures/<int:pk>/original/", views.PictureOriginalView.as_view(), name="picture-original"),
    # Cndr
    path("cndr/", views.CndrListView.as_view(), name="cndr-list"),
    path("cndr/<int:pk>/", views.CndrDetailView.as_view(), name="cndr-detail"),
    # Version
    path("version/", views.VersionView.as_view(), name="version"),
]

urlpatterns = [
    path("", health),
    path("admin/", admin.site.urls),
    path("api/", include((api_urlpatterns, "api"))),
    # TODO: Remove legacy URLs once all clients have been updated.
    path("", include("pnogo.legacy_urls")),
]
