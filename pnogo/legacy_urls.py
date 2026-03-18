"""
Legacy URL mappings for backwards compatibility with the old Flask API.

TODO: Remove this file (and legacy.py) once all clients have been updated.
      Then remove the include("pnogo.legacy_urls") line from pnogo/urls.py.
"""

from django.urls import path

from . import legacy

urlpatterns = [
    # List
    path("getall", legacy.LegacyGetAllView.as_view()),
    path("getall/<str:cndr>", legacy.LegacyGetAllView.as_view()),
    path("getallpnoghi", legacy.LegacyGetAllPnoghiView.as_view()),
    # Info
    path("info", legacy.LegacyInfoView.as_view()),
    path("infopnogo", legacy.LegacyInfoView.as_view()),
    # Description
    path("desc", legacy.LegacyDescView.as_view()),
    path("descpnogo", legacy.LegacyDescView.as_view()),
    # Delete
    path("kill", legacy.LegacyKillView.as_view()),
    path("killpnogo", legacy.LegacyKillView.as_view()),
    # Image serving
    path("get", legacy.LegacyGetView.as_view()),
    path("getpnogo", legacy.LegacyGetView.as_view()),
    path("getstretched", legacy.LegacyGetStretchedView.as_view()),
    path("getstretchedpnogo", legacy.LegacyGetStretchedView.as_view()),
    path("getbitmap", legacy.LegacyGetBitmapView.as_view()),
    path("getoriginal", legacy.LegacyGetOriginalView.as_view()),
    path("getpnogoriginal", legacy.LegacyGetOriginalView.as_view()),
    # Random
    path("random", legacy.LegacyRandomView.as_view()),
    path("random/<str:cndr>", legacy.LegacyRandomView.as_view()),
    path("randompnogo", legacy.LegacyRandomPnogoView.as_view()),
    # Daily
    path("daily", legacy.LegacyDailyView.as_view()),
    path("dailypnogo", legacy.LegacyDailyView.as_view()),
    # Count
    path("count", legacy.LegacyCountView.as_view()),
    path("count/<str:cndr>", legacy.LegacyCountView.as_view()),
    path("countpnogo", legacy.LegacyCountPnogoView.as_view()),
    # Upload
    path("add/<str:cndr>", legacy.LegacyAddView.as_view()),
    path("addpnogo", legacy.LegacyAddView.as_view()),
    # Cndr management
    path("create", legacy.LegacyCreateCndrView.as_view()),
    path("remove", legacy.LegacyRemoveCndrView.as_view()),
    path("list", legacy.LegacyListCndrView.as_view()),
    # Version
    path("version", legacy.LegacyVersionView.as_view()),
    # Update (stub, was already useless)
    path("update", legacy.LegacyUpdateView.as_view()),
]
