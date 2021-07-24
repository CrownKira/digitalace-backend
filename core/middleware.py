from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _


from rest_framework import status


class ExceptionMiddleware(object):
    """
    Middleware that makes sure clients see a meaningfull error message wrapped in a Json response.
    https://stackoverflow.com/questions/44229783/catch-protected-error-and-show-its-message-to-the-user-instead-of-bare-500-code/44231197
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):

        data = {
            "code": "server_error",
            "message": _("Internal server error."),
            "error": {"type": str(type(exception)), "message": str(exception)},
        }

        return JsonResponse(data=data, status=status.HTTP_400_BAD_REQUEST)
