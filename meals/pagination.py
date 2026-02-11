from rest_framework.pagination import PageNumberPagination

class MyPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'size'   # المستخدم يحدد العدد
    max_page_size = 50
