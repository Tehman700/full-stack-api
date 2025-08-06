from quickstart.models.signals_model import ErrorLog

def log_error(request, message, status_code=None):
    user = request.user if request.user.is_authenticated else None
    ErrorLog.objects.create(
        user=user,
        path=request.path,
        method=request.method,
        message= message,
        status_code=status_code
    )
