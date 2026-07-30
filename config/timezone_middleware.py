import pytz
from django.utils import timezone


class ForceISTTimeZone:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ist = pytz.timezone('Asia/Kolkata')
        timezone.activate(ist)
        response = self.get_response(request)
        timezone.deactivate()
        return response
