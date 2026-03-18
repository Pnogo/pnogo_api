import importlib.metadata
from datetime import date

from django.db.models import F
from django.http import FileResponse, HttpResponse
from django.utils.text import get_valid_filename
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cndr, Picture
from .serializers import CndrSerializer, PictureSerializer, PictureUpdateSerializer, PictureUploadSerializer
from .services import images, storage

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Pictures CRUD ---


class PictureListView(generics.ListAPIView):
    serializer_class = PictureSerializer

    def get_queryset(self):
        qs = Picture.objects.select_related("cndr").all()
        cndr = self.request.query_params.get("cndr")
        if cndr:
            qs = qs.filter(cndr__name__iexact=cndr)
        return qs


class PictureDetailView(APIView):
    def get(self, request, pk):
        try:
            picture = Picture.objects.select_related("cndr").get(pk=pk)
        except Picture.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(PictureSerializer(picture).data)

    def patch(self, request, pk):
        serializer = PictureUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = Picture.objects.filter(pk=pk).update(description=serializer.validated_data["description"])
        if not updated:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "description updated"})

    def delete(self, request, pk):
        try:
            picture = Picture.objects.get(pk=pk)
        except Picture.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        storage.delete_object(picture.file)
        picture.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PictureUploadView(APIView):
    def post(self, request):
        serializer = PictureUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded = serializer.validated_data["picture"]
        cndr_name = serializer.validated_data["cndr"]
        description = serializer.validated_data.get("description", "")

        filename = get_valid_filename(uploaded.name)
        if not allowed_file(filename):
            return Response({"detail": "file type not allowed"}, status=status.HTTP_400_BAD_REQUEST)

        if Picture.objects.filter(file=filename).exists():
            return Response({"detail": f"{filename} already present"}, status=status.HTTP_409_CONFLICT)

        try:
            cndr = Cndr.objects.get(name__iexact=cndr_name)
        except Cndr.DoesNotExist:
            return Response({"detail": f"cndr '{cndr_name}' not found"}, status=status.HTTP_404_NOT_FOUND)

        storage.put_object(filename, uploaded)
        picture = Picture.objects.create(file=filename, cndr=cndr, description=description)
        return Response(PictureSerializer(picture).data, status=status.HTTP_201_CREATED)


class PictureCountView(APIView):
    def get(self, request):
        qs = Picture.objects.all()
        cndr = request.query_params.get("cndr")
        if cndr:
            qs = qs.filter(cndr__name__iexact=cndr)
        return Response({"count": qs.count()})


# --- Image serving ---


class PictureImageView(APIView):
    def get(self, request, pk):
        try:
            picture = Picture.objects.get(pk=pk)
        except Picture.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        width = request.query_params.get("width")
        height = request.query_params.get("height")
        maxsize = request.query_params.get("maxsize", 1280)

        obj = storage.get_object(picture.file)
        buf = images.resize_image(obj, width=width, height=height, maxsize=int(maxsize))
        Picture.objects.filter(pk=pk).update(sent=F("sent") + 1)
        return FileResponse(buf, content_type="image/jpeg")


class PictureStretchedView(APIView):
    def get(self, request, pk):
        try:
            picture = Picture.objects.get(pk=pk)
        except Picture.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        maxsize = int(request.query_params.get("maxsize", 1920))
        obj = storage.get_object(picture.file)
        buf = images.stretch_image(obj, maxsize=maxsize)
        Picture.objects.filter(pk=pk).update(sent=F("sent") + 1)
        return FileResponse(buf, content_type="image/jpeg")


class PictureBitmapView(APIView):
    def get(self, request, pk):
        try:
            picture = Picture.objects.get(pk=pk)
        except Picture.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        width = request.query_params.get("width", 128)
        height = request.query_params.get("height", 64)
        obj = storage.get_object(picture.file)
        data = images.to_bitmap(obj, width=int(width), height=int(height))
        Picture.objects.filter(pk=pk).update(sent=F("sent") + 1)
        return HttpResponse(data, content_type="text/plain")


class PictureOriginalView(APIView):
    def get(self, request, pk):
        try:
            picture = Picture.objects.get(pk=pk)
        except Picture.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        obj = storage.get_object(picture.file)
        return FileResponse(obj, content_type="image/jpeg")


# --- Special endpoints ---


class PictureRandomView(APIView):
    def get(self, request):
        qs = Picture.objects.select_related("cndr").all()
        cndr = request.query_params.get("cndr")
        if cndr:
            qs = qs.filter(cndr__name__iexact=cndr)
        picture = qs.order_by("?").first()
        if not picture:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(PictureSerializer(picture).data)


class PictureDailyView(APIView):
    def get(self, request):
        today = date.today()

        picture = Picture.objects.filter(daily_date=today).order_by("?").first()
        if picture is None:
            picture = Picture.objects.filter(daily_date__isnull=True).order_by("?").first()
            if picture is None:
                Picture.objects.all().update(daily_date=None)
                picture = Picture.objects.filter(daily_date__isnull=True).order_by("?").first()

        if picture is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        Picture.objects.filter(pk=picture.pk).update(daily_date=today)
        picture.refresh_from_db()
        return Response(PictureSerializer(picture).data)


# --- Cndr ---


class CndrListView(generics.ListCreateAPIView):
    queryset = Cndr.objects.all()
    serializer_class = CndrSerializer


class CndrDetailView(APIView):
    def delete(self, request, pk):
        try:
            cndr = Cndr.objects.get(pk=pk)
        except Cndr.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if cndr.pictures.exists():
            return Response(
                {"detail": "cannot delete: cndr still has pictures"},
                status=status.HTTP_409_CONFLICT,
            )
        cndr.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Version ---


class VersionView(APIView):
    def get(self, request):
        try:
            version = importlib.metadata.version("pnogo-api")
        except importlib.metadata.PackageNotFoundError:
            version = "dev"
        return Response({"version": version})
