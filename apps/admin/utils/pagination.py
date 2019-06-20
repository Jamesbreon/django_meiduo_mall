from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MyPage(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'pagesize'
    page_size = 2
    max_page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'lists': data,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
            'pagesize': self.page_size
        })
