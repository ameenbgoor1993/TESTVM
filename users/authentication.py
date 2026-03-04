from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import VolunteerToken

class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'

class VolunteerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        try:
            token = VolunteerToken.objects.get(key=key)
        except VolunteerToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        if not token.volunteer.is_active:
            raise AuthenticationFailed('User inactive or deleted.')

        return (token.volunteer, token)

