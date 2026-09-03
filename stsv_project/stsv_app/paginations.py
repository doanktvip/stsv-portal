from rest_framework import pagination


class MasterDataPaginator(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 100


class StandardMobilePaginator(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 50
