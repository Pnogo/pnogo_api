from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed


class TokenQueryParamAuthentication(TokenAuthentication):
    """
    DRF TokenAuthentication extended to also accept:
    - X-API-Key header
    - ?key= query param (legacy)

    Falls back to the standard Authorization: Token <key> header.
    """

    def authenticate(self, request):
        # Try X-API-Key header or ?key= query param first
        key = request.META.get("HTTP_X_API_KEY") or request.query_params.get("key")
        if key:
            return self.authenticate_credentials(key)

        # Fall back to standard "Authorization: Token <key>" header
        return super().authenticate(request)

    def authenticate_credentials(self, key):
        try:
            token = Token.objects.select_related("user").get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Invalid API key.")

        if not token.user.is_active:
            raise AuthenticationFailed("User inactive.")

        return (token.user, token)
