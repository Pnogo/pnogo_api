"""
Legacy adapter views that map old Flask-style endpoints to new Django views.

TODO: Remove this file (and legacy_urls.py) once all clients have been updated.
"""

import json

from django.http import HttpResponse
from markupsafe import escape
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cndr, Picture
from .serializers import PictureSerializer
from .services import storage
from .views import (
    PictureBitmapView,
    PictureCountView,
    PictureDailyView,
    PictureImageView,
    PictureListView,
    PictureOriginalView,
    PictureRandomView,
    PictureStretchedView,
    PictureUploadView,
    VersionView,
)

# --- Helpers ---


def _id_from_query(request):
    """Extract ?id= and return as int, or None."""
    pnid = request.query_params.get("id")
    return int(pnid) if pnid is not None else None


# --- /getall, /getall/<cndr>, /getallpnoghi ---


class LegacyGetAllView(PictureListView):
    """GET /getall and GET /getall/<cndr>"""

    def get_queryset(self):
        qs = Picture.objects.select_related("cndr").all()
        cndr = self.kwargs.get("cndr") or self.request.query_params.get("cndr")
        if cndr:
            qs = qs.filter(cndr__name__iexact=cndr)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # Old API used "name" instead of "cndr"
        data = serializer.data
        for item in data:
            if "cndr" in item:
                item["name"] = item.pop("cndr")
        return HttpResponse(json.dumps(data), content_type="application/json")


class LegacyGetAllPnoghiView(LegacyGetAllView):
    """GET /getallpnoghi — hardcoded alias for cndr=pongo."""

    def get_queryset(self):
        return Picture.objects.select_related("cndr").filter(cndr__name__iexact="pongo")


# --- /info, /infopnogo ---


class LegacyInfoView(APIView):
    """GET /info?id=<id>"""

    def get(self, request):
        pk = _id_from_query(request)
        if pk is None:
            return Response(status=400)
        try:
            picture = Picture.objects.select_related("cndr").get(pk=pk)
        except Picture.DoesNotExist:
            return Response(status=404)
        data = PictureSerializer(picture).data
        # Old API used "name" instead of "cndr"
        data["name"] = data.pop("cndr")
        return Response(data)


# --- /desc, /descpnogo ---


class LegacyDescView(APIView):
    """GET /desc?id=<id>&description=<desc>"""

    def get(self, request):
        pk = _id_from_query(request)
        desc = request.query_params.get("description", "")
        if pk is None:
            return Response(status=400)
        updated = Picture.objects.filter(pk=pk).update(description=desc)
        if not updated:
            return Response(status=404)
        return HttpResponse(f"done! set desc of {pk} to: {desc}")


# --- /kill, /killpnogo ---


class LegacyKillView(APIView):
    """GET /kill?id=<id>"""

    def get(self, request):
        pk = _id_from_query(request)
        if pk is None:
            return Response(status=400)
        try:
            picture = Picture.objects.get(pk=pk)
        except Picture.DoesNotExist:
            return Response(status=404)
        storage.delete_object(picture.file)
        picture.delete()
        return HttpResponse(f"success!<br>il pongo numero {pk} è stato abbattuto, pace all'anima sua")


# --- /get, /getpnogo ---


class LegacyGetView(PictureImageView):
    """GET /get?id=<id>&width=...&height=...&maxsize=..."""

    def get(self, request):
        pk = _id_from_query(request)
        if pk is None:
            return Response(status=400)
        return super().get(request, pk=pk)


# --- /getstretched, /getstretchedpnogo ---


class LegacyGetStretchedView(PictureStretchedView):
    """GET /getstretched?id=<id>&maxsize=..."""

    def get(self, request):
        pk = _id_from_query(request)
        if pk is None:
            return Response(status=400)
        return super().get(request, pk=pk)


# --- /getbitmap ---


class LegacyGetBitmapView(PictureBitmapView):
    """GET /getbitmap?id=<id>&width=...&height=..."""

    def get(self, request):
        pk = _id_from_query(request)
        if pk is None:
            return Response(status=400)
        return super().get(request, pk=pk)


# --- /getoriginal, /getpnogoriginal ---


class LegacyGetOriginalView(PictureOriginalView):
    """GET /getoriginal?id=<id>"""

    def get(self, request):
        pk = _id_from_query(request)
        if pk is None:
            return Response(status=400)
        return super().get(request, pk=pk)


# --- /random, /random/<cndr>, /randompnogo ---


class LegacyRandomView(PictureRandomView):
    """GET /random and GET /random/<cndr>"""

    def get(self, request, cndr=None):
        if cndr:
            request.query_params._mutable = True
            request.query_params["cndr"] = cndr
            request.query_params._mutable = False
        response = super().get(request)
        if hasattr(response, "data") and "cndr" in response.data:
            response.data["name"] = response.data.pop("cndr")
        return response


class LegacyRandomPnogoView(LegacyRandomView):
    """GET /randompnogo"""

    def get(self, request):
        return super().get(request, cndr="pongo")


# --- /daily, /dailypnogo ---


class LegacyDailyView(PictureDailyView):
    """GET /daily — same logic, just remap 'cndr' → 'name' in response."""

    def get(self, request):
        response = super().get(request)
        if hasattr(response, "data") and "cndr" in response.data:
            response.data["name"] = response.data.pop("cndr")
        return response


# --- /count, /count/<cndr>, /countpnogo ---


class LegacyCountView(PictureCountView):
    """GET /count and GET /count/<cndr>"""

    def get(self, request, cndr=None):
        if cndr:
            request.query_params._mutable = True
            request.query_params["cndr"] = cndr
            request.query_params._mutable = False
        return super().get(request)


class LegacyCountPnogoView(LegacyCountView):
    """GET /countpnogo"""

    def get(self, request):
        return super().get(request, cndr="pongo")


# --- /add/<cndr>, /addpnogo ---


class LegacyAddView(PictureUploadView):
    """GET+POST /add/<cndr> — GET returns HTML form, POST uploads."""

    def get(self, request, cndr="pongo"):
        return HttpResponse(
            f"""
            <!doctype html>
            <title>Upload new {escape(cndr)}</title>
            <h1>Upload new {escape(cndr)}</h1>
            <form method=post enctype=multipart/form-data>
              <input type=file name=picture>
              <input type=submit value=Upload>
            </form>
            """,
            content_type="text/html",
        )

    def post(self, request, cndr="pongo"):
        # Inject cndr into request data so the parent serializer picks it up
        request.data._mutable = True
        request.data["cndr"] = cndr
        request.data._mutable = False
        response = super().post(request)
        if response.status_code == 201:
            return HttpResponse("done!")
        return response


# --- /create ---


class LegacyCreateCndrView(APIView):
    """GET /create?name=<name>"""

    def get(self, request):
        name = request.query_params.get("name", "")
        if not name:
            return Response(status=400)
        _, created = Cndr.objects.get_or_create(name=escape(name))
        return HttpResponse("done" if created else f"morte: {escape(name)} already present in db")


# --- /remove ---


class LegacyRemoveCndrView(APIView):
    """GET /remove?name=<name>"""

    def get(self, request):
        name = request.query_params.get("name", "")
        if not name:
            return Response(status=400)
        try:
            cndr = Cndr.objects.get(name__iexact=name)
        except Cndr.DoesNotExist:
            return Response(status=404)
        if cndr.pictures.exists():
            return HttpResponse(f"morte: some pictures of {escape(name)} are still in the db")
        cndr.delete()
        return HttpResponse("done")


# --- /list ---


class LegacyListCndrView(APIView):
    """GET /list — returns JSON array of {id, name}."""

    def get(self, request):
        cndrs = list(Cndr.objects.values("id", "name"))
        return HttpResponse(json.dumps(cndrs), content_type="application/json")


# --- /version ---

LegacyVersionView = VersionView


# --- /update (stub, was already marked useless) ---


class LegacyUpdateView(APIView):
    def get(self, request):
        return Response({"added": 0, "removed": 0})
