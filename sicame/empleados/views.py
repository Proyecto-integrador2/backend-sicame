from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse
from .models import Empleado
import face_recognition

class RegistrarEmpleadoAPIView(APIView):
    """
    Vista que permite registrar la información y los face encodings del empleado

    - Recibe una solictud POST con los datos y el rostro del empleado
    - Carga la imagen a un formato válido para la libreria face_recognition
    - Extrae el encoding facial usando la libreria mencionada
    - Si la información y el proceso del tros están en orden, hace el registro del usuario

    Args:
        request: La solicitud HTTP que contiene los datos del empleado y la imagen
    Returns:
        JsonResponse: Respuesta en formato JSON con el estado de la operación.
    """
    def post(self, request, *args, **kwargs):
        data = request.data
        imagen = request.FILES.get('foto')

        if not imagen:
            return JsonResponse({'error': 'No se envió una imagen'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            imagen = face_recognition.load_image_file(imagen)
            encodings = face_recognition.face_encodings(imagen)

            if len(encodings) == 0:
                return JsonResponse({'error': 'No se encontró un rostro en la imagen'}, status=status.HTTP_400_BAD_REQUEST)

            encoding = encodings[0]

            empleado = Empleado.objects.create(
                nombre=data.get('nombre'),
                correo=data.get('correo'),
                cargo=data.get('cargo')
            )
            empleado.set_caracteristicas_faciales(encoding)
            empleado.save()

            return JsonResponse({'success': 'Empleado registrado correctamente'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
