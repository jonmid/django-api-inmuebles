from django.shortcuts import get_object_or_404
from rest_framework.decorators import permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework import generics, mixins
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from inmuebleslist_app.api.permissions import IsAdminOrReadOnly, IsComentarioUserOrReadOnly
from inmuebleslist_app.models import Inmueble, Empresa, Comentario
from inmuebleslist_app.api.serializers import InmuebleSerializer, EmpresaSerializer, ComentarioSerializer
from inmuebleslist_app.api.throttling import ComentarioCreateThrottle, ComentarioListThrottle
from inmuebleslist_app.api.pagination import InmuebleLimitOffsetPagination, InmueblePagination

class UsuarioComentario(generics.ListAPIView):
  serializer_class = ComentarioSerializer

  # {{ _.url }}/tienda/inmueble/comentarios/jonmid
  # def get_queryset(self):
  #   username = self.kwargs['username']
  #   return Comentario.objects.filter(comentario_user__username=username)
  
  # {{ _.url }}/tienda/inmueble/comentarios/?username=jonmid
  def get_queryset(self):
    username = self.request.query_params.get('username')
    return Comentario.objects.filter(comentario_user__username=username)


class ComentarioList(generics.ListCreateAPIView):
  # queryset = Comentario.objects.all()
  serializer_class = ComentarioSerializer
  permission_classes = [IsAuthenticated]
  throttle_classes = [ComentarioListThrottle, AnonRateThrottle]
  filter_backends = [DjangoFilterBackend]
  filterset_fields = ['comentario_user__username', 'activo']

  # Sobre-escribe el queryset para personalizarlo
  # {{ _.url }}/tienda/inmueble/1/comentario/?comentario_user__username=prueba&activo=true
  def get_queryset(self):
    pk = self.kwargs['pk']
    return Comentario.objects.filter(inmueble=pk)


class ComentarioCreate(generics.CreateAPIView):
  serializer_class = ComentarioSerializer
  permission_classes = [IsAuthenticated]
  throttle_classes = [ComentarioCreateThrottle]

  def get_queryset(self):
    return Comentario.objects.all()

  def perform_create(self, serializer):
    pk = self.kwargs.get('pk')
    inmueble = Inmueble.objects.get(pk=pk)

    user = self.request.user
    comentario_queryset = Comentario.objects.filter(inmueble=inmueble, comentario_user=user)

    if comentario_queryset.exists():
      raise ValidationError('El usuario ya escribio un comentario para este Inmueble')
    
    if inmueble.numero_calificacion == 0:
      inmueble.avg_calificacion = serializer.validated_data['calificacion']
    else:
      inmueble.avg_calificacion = (serializer.validated_data['calificacion'] + inmueble.avg_calificacion) / 2
    
    inmueble.numero_calificacion = inmueble.numero_calificacion + 1
    inmueble.save()

    serializer.save(inmueble=inmueble, comentario_user=user)


class ComentarioDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Comentario.objects.all()
  serializer_class = ComentarioSerializer
  permission_classes = [IsComentarioUserOrReadOnly]
  throttle_classes = [ScopedRateThrottle]
  throttle_scope = 'comentario-detail'

# class ComentarioList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
#   queryset = Comentario.objects.all()
#   serializer_class = ComentarioSerializer

#   def get(self, request, *args, **kwargs):
#     return self.list(request, *args, **kwargs)
  
#   def post(self, request, *args, **kwargs):
#     return self.create(request, *args, **kwargs)


# class ComentarioDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
#   queryset = Comentario.objects.all()
#   serializer_class = ComentarioSerializer

#   def get(self, request, *args, **kwargs):
#     return self.retrieve(request, *args, **kwargs)


class EmpresaVS(viewsets.ModelViewSet):
  # Bloquea el acceso solo a este EndPoint (Se debe logear)
  # permission_classes = [IsAuthenticated] # Opcion 1
  permission_classes = [IsAdminOrReadOnly] # Opcion 2 (personalizado)
  queryset = Empresa.objects.all()
  serializer_class = EmpresaSerializer


# class EmpresaVS(viewsets.ViewSet):
#   def list(self, request):
#     queryset = Empresa.objects.all()
#     serializer = EmpresaSerializer(queryset, many=True)
#     return Response(serializer.data)
  
#   def retrieve(self, request, pk=None):
#     queryset = Empresa.objects.all()
#     inmueblelist = get_object_or_404(queryset, pk=pk)
#     serializer = EmpresaSerializer(inmueblelist)
#     return Response(serializer.data)
  
#   def create(self, request):
#     serializer = EmpresaSerializer(data=request.data)
#     if serializer.is_valid():
#       serializer.save()
#       return Response(serializer.data)
#     else:
#       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
#   def update(self, request, pk):
#     try:
#       empresa = Empresa.objects.get(pk=pk)
#     except Empresa.DoesNotExist:
#       return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
#     serializer = EmpresaSerializer(empresa, data=request.data)
#     if serializer.is_valid():
#       serializer.save()
#       return Response(serializer.data)
#     else:
#       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
#   def destroy(self, request, pk):
#     try:
#       empresa = Empresa.objects.get(pk=pk)
#     except Empresa.DoesNotExist:
#       return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
      
#     empresa.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)


class EmpresaAV(APIView):
  permission_classes = [IsAdminOrReadOnly]

  def get(self, request):
    empresas = Empresa.objects.all()
    serializer = EmpresaSerializer(empresas, many=True, context={'request': request})
    return Response(serializer.data)

  def post(self, request):
    serializer = EmpresaSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmpresaDetalleAV(APIView):
  def get(self, request, pk):
    try:
      empresa = Empresa.objects.get(pk=pk)
      serializer = EmpresaSerializer(empresa, context={'request': request})
      return Response(serializer.data)
    except Empresa.DoesNotExist:
      return Response({'Error':'La empresa no existe'}, status=status.HTTP_404_NOT_FOUND)
  
  def put(self, request, pk):
    empresa = Empresa.objects.get(pk=pk)
    de_serializer = EmpresaSerializer(empresa, data=request.data)
    if de_serializer.is_valid():
      de_serializer.save()
      return Response(de_serializer.data)
    else:
      return Response(de_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  def delete(self, request, pk):
    try:
      empresa = Empresa.objects.get(pk=pk)
      empresa.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)
    except Empresa.DoesNotExist:
      return Response({'Error':'La empresa no existe'}, status=status.HTTP_404_NOT_FOUND)


class InmuebleList(generics.ListAPIView):
  queryset = Inmueble.objects.all()
  serializer_class = InmuebleSerializer
  filter_backends = [filters.SearchFilter, filters.OrderingFilter]
  search_fields = ['direccion', 'empresa__nombre']
  pagination_class = InmueblePagination
  # pagination_class = InmuebleLimitOffsetPagination # Utilizar esta paginacion
  # {{ _.url }}/tienda/inmueble/list/?search=sas&ordering=direccion # ASC
  # {{ _.url }}/tienda/inmueble/list/?search=sas&ordering=-direccion # DESC


class InmuebleListAV(APIView):
  def get(self, request):
    # Lista todos los inmuebles
    inmuebles = Inmueble.objects.all()
    serializer = InmuebleSerializer(inmuebles, many=True)
    return Response(serializer.data)

  def post(self, request):
    # Guarda un nuevo inmueble
    serializer = InmuebleSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InmuebleDetalleAV(APIView):
  permission_classes = [IsAdminOrReadOnly]

  def get(self, request, pk):
    # Lista solo UN inmueble
    try:
      inmueble = Inmueble.objects.get(pk=pk)
      serializer = InmuebleSerializer(inmueble)
      return Response(serializer.data)
    except Inmueble.DoesNotExist:
      return Response({'Error':'El inmueble no existe'}, status=status.HTTP_404_NOT_FOUND)
  
  def put(self, request, pk):
    # Actualiza un inmueble
    inmueble = Inmueble.objects.get(pk=pk)
    de_serializer = InmuebleSerializer(inmueble, data=request.data)
    if de_serializer.is_valid():
      de_serializer.save()
      return Response(de_serializer.data)
    else:
      return Response(de_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  def delete(self, request, pk):
    # Elimina un inmueble
    try:
      inmueble = Inmueble.objects.get(pk=pk)
      inmueble.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)
    except Inmueble.DoesNotExist:
      return Response({'Error':'El inmueble no existe'}, status=status.HTTP_404_NOT_FOUND)