from django.utils import translation


class ForceDashboardArabicMiddleware:
    """
    Forces Arabic language for all dashboard and chart API endpoints.
    This ensures error messages are always returned in Arabic,
    regardless of the Accept-Language header.
    """
    ARABIC_PATHS = ['/dashboard/', '/charts/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if any(path in request.path for path in self.ARABIC_PATHS):
            translation.activate('ar')
            request.LANGUAGE_CODE = 'ar'

        response = self.get_response(request)
        return response
