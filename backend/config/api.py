from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def success_response(data=None, *, message=None, status=200, pagination=None):
    payload = {
        "success": True,
        "data": data,
    }
    if message:
        payload["message"] = message
    if pagination:
        payload["pagination"] = pagination
    return Response(payload, status=status)


def error_response(message, *, status=400, code=None, errors=None):
    payload = {
        "success": False,
        "message": message,
    }
    if code:
        payload["code"] = code
    if errors is not None:
        payload["errors"] = errors
    return Response(payload, status=status)


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "data": data,
                "pagination": {
                    "page": self.page.number,
                    "page_size": self.get_page_size(self.request),
                    "total": self.page.paginator.count,
                    "pages": self.page.paginator.num_pages,
                },
            }
        )
