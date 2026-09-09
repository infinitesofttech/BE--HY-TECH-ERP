from rest_framework.pagination import PageNumberPagination


class OptionalPageNumberPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500

    def paginate_queryset(self, queryset, request, view=None):
        # If client did not explicitly request 'page', return raw unpaginated list
        if 'page' not in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)
