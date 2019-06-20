from rest_framework.pagination import PageNumberPagination


class PagNum(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'pagesize'
    page_size = 1
    max_page_size = 2
