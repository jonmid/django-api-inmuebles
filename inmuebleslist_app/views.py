# from django.http import JsonResponse
# from django.shortcuts import render
# from inmuebleslist_app.models import Inmueble


# # Lista todos los inmuebles
# def inmueble_list(request):
#   inmuebles = Inmueble.objects.all()
#   data = {
#     'inmuebles': list(inmuebles.values())
#   }
#   return JsonResponse(data)


# # Lista solo UN inmueble
# def inmueble_detalle(request, id):
#   inmueble = Inmueble.objects.get(pk=id)
#   data = {
#     'direccion': inmueble.direccion,
#     'pais': inmueble.pais,
#   }
#   return JsonResponse(data)