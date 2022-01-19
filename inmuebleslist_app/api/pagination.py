from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

class InmueblePagination(PageNumberPagination):
  # Total de registros por pagina
  page_size = 1
  # Nombre del parametro para seleccionar la pagina (?p=2)
  page_query_param = 'p'
  # Nombre del parametro para seleccionar la cantidad de registros en la pagina (?p=1&size=3)
  page_size_query_param = 'size'
  # Tamaño maximo de registros por pagina
  max_page_size = 10
  # Me devuelve la ultima pagina (?p=end)
  last_page_strings = 'end'


class InmuebleLimitOffsetPagination(LimitOffsetPagination):
  # ?limit=1&offset=0
  default_limit = 1