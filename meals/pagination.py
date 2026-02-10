from rest_framework.pagination import PageNumberPagination

class MyPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'   # المستخدم يحدد العدد
    max_page_size = 50
