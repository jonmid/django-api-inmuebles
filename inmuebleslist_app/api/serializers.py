from django.db.models import fields
from rest_framework import serializers, validators
from inmuebleslist_app.models import Inmueble, Empresa, Comentario


# ***** OPCION 1 (utilizar esta opcion)
class ComentarioSerializer(serializers.ModelSerializer):
  comentario_user = serializers.StringRelatedField(read_only=True)
  
  class Meta:
    model = Comentario
    # fields = "__all__"
    exclude = ['inmueble']


class InmuebleSerializer(serializers.ModelSerializer):
  comentarios = ComentarioSerializer(many=True, read_only=True)
  longitud_direccion = serializers.SerializerMethodField()
  empresa_nombre = serializers.CharField(source='empresa.nombre')

  class Meta:
    model = Inmueble
    fields = "__all__" # Muestra todos los campos
    # fields = ['direccion','pais','imagen','activo'] # Muestra algunos campos
    # exclude = ['id'] # Excluye campos al mostrar
  
  def get_longitud_direccion(self, object):
    cantidad_caracteres = len(object.direccion)
    return cantidad_caracteres
  
  def validate(self, data):
    if data['direccion'] == data['pais']:
      raise serializers.ValidationError('La direccion y el pais deben ser diferentes')
    else:
      return data

  def validate_imagen(self, data):
    if len(data) <= 2:
      raise serializers.ValidationError('La URL de la imagen es muy corta')
    else:
      return data


# class EmpresaSerializer(serializers.HyperlinkedModelSerializer):
class EmpresaSerializer(serializers.ModelSerializer):
  inmueblelist = InmuebleSerializer(many=True, read_only=True)
  # inmueblelist = serializers.StringRelatedField(many=True)
  # inmueblelist = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
  # inmueblelist = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name="inmueble-detail",lookup_field='id')

  class Meta:
    model = Empresa
    fields = "__all__"


# ***** OPCION 2
# def column_longitud(value):
#   if len(value) <= 2:
#     raise serializers.ValidationError("El valor es demasiado corto")

# class InmuebleSerializer(serializers.Serializer):
#   id = serializers.IntegerField(read_only=True)
#   direccion = serializers.CharField(validators=[column_longitud])
#   pais = serializers.CharField(validators=[column_longitud])
#   descripcion = serializers.CharField()
#   imagen = serializers.CharField()
#   activo = serializers.BooleanField()
  
#   def create(self, validated_data):
#     return Inmueble.objects.create(**validated_data)
  
#   def update(self, instance, validated_data):
#     instance.direccion = validated_data.get('direccion', instance.direccion)
#     instance.pais = validated_data.get('pais', instance.pais)
#     instance.descripcion = validated_data.get('descripcion', instance.descripcion)
#     instance.imagen = validated_data.get('imagen', instance.imagen)
#     instance.activo = validated_data.get('activo', instance.activo)
#     instance.save()
#     return instance
  
#   def validate(self, data):
#     if data['direccion'] == data['pais']:
#       raise serializers.ValidationError('La direccion y el pais deben ser diferentes')
#     else:
#       return data
  
#   def validate_imagen(self, data):
#     if len(data) <= 2:
#       raise serializers.ValidationError('La URL de la imagen es muy corta')
#     else:
#       return data