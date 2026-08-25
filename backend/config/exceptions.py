from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    if isinstance(response.data, dict) and "detail" in response.data:
        response.data = {
            "success": False,
            "message": response.data["detail"],
        }
        return response

    if response.status_code in {status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY}:
        response.data = {
            "success": False,
            "message": "Validation failed.",
            "errors": response.data,
        }
        return response

    response.data = {
        "success": False,
        "message": "Request failed.",
        "errors": response.data,
    }
    return response
