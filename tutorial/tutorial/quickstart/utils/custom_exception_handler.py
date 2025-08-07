from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied
from quickstart.utils.response_handler import ResponseHandler
from quickstart.utils.logger import log_error


def custom_exception_handler(exc, context):
    request = context.get('request')

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):

        log_error(request, "Authentication credentials are missing or invalid", 200)
        return ResponseHandler.error(
            message="Authentication credentials are missing or invalid.",
            code=-1,
            errors=str(exc)
        )

    if isinstance(exc, PermissionDenied):
        log_error(request, "Dont have permission to perform action", 200)
        return ResponseHandler.error(
            message="You do not have permission to perform this action.",
            code=-2,
            errors=str(exc)
        )

    # Handle other exceptions using default DRF handler
    return exception_handler(exc, context)
