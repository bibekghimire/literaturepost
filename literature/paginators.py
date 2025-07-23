from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound

class CustomPaginator(PageNumberPagination):
    page_size=5 #default
    page_size_query_param= 'page_size'
    max_page_size= 500
    allowed_page_size=[5,10,50,100,500]
    def get_page_size(self,request):
        page_size = request.query_params.get(self.page_size_query_param) 
        if page_size:
            try:
                page_size=int(page_size)
            except ValueError:
                raise NotFound(detail= f"Invalid page size:Must be an integer")
            if page_size not in self.allowed_page_size:
                raise NotFound(
                    detail= f"Invalid page size. Allowed values: {self.allowed_page_size}"
                )
            return page_size
        return self.page_size #fallback return default
