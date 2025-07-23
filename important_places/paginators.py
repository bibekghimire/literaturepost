from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound

class CustomPaginator(PageNumberPagination):
    page_size_query_param='page_size'

    def get_page_size(self, request):
        page_size = request.query_params.get(self.page_size_query_param)
        if page_size:
            try:
                page_size=int(page_size)
            except ValueError:
                raise NotFound(detail= f"Invalid page size:Must be an integer")
            if page_size in [10,50,100,500]:
                return request.kwargs('page_size')
        return 10
        