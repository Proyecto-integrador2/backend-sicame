from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse
from .models import Empleado, Asistencia
import face_recognition
from google.cloud import vision
import base64
import requests
import tempfile
from PIL import Image
import numpy as np

API_KEY = "AIzaSyDnS9eZlylQSIxsWBGc6AGDhqy55fYv2u0" #poner en el .env

def analyze_emotion(image_path):
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image_base64 = base64.b64encode(content).decode('utf-8')
    url = f'https://vision.googleapis.com/v1/images:annotate?key={API_KEY}'
    headers = {'Content-Type': 'application/json'}
    body = {
        "requests": [
            {
                "image": {
                    "content": image_base64
                },
                "features": [
                    {
                        "type": "FACE_DETECTION"
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)
    response_data = response.json()

    if 'error' in response_data:
        raise Exception(response_data['error']['message'])

    faces = response_data['responses'][0].get('faceAnnotations', [])
    emotions = []
    for face in faces:
        emotions.append({
            'joy': face.get('joyLikelihood'),
            'sorrow': face.get('sorrowLikelihood'),
            'anger': face.get('angerLikelihood'),
            'surprise': face.get('surpriseLikelihood')
        })

    return emotions

class RegistrarEmpleadoAPIView(APIView):
    """
    Vista que permite registrar la información y los face encodings del empleado

    - Recibe una solictud POST con los datos y el rostro del empleado
    - Carga la imagen a un formato válido para la libreria face_recognition
    - Extrae el encoding facial usando la libreria mencionada
    - Si la información y el proceso del tros están en orden, hace el registro del usuario

    Args:
        request: La solicitud HTTP que contiene los datos del empleado y la foto
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


class MarcarAsistenciaAPIView(APIView):
    """
    Vista que permite marcas asistencia por medio del rostro del empleado

    - Recibe una solictud POST con los datos de asistencia y el rostro del empleado
    - Carga la imagen a un formato válido para la libreria face_recognition
    - Extrae el encoding facial del rostro entrante
    - Busca si hay un empleado con el cual el encoding haga match
    - Si hay match, guarda la asistencia en el sistema con los datos del empleado correspondiente

    Args:
        request: La solicitud HTTP que contiene los datos de asistencia y la foto
    Returns:
        JsonResponse: Respuesta en formato JSON con el estado de la operación.
    """
    def post(selfself, request, *args, **kwargs):
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

            empleados = Empleado.objects.all()
            for empleado in empleados:
                empleado_encoding = empleado.get_caracteristicas_faciales()
                emparejamiento = face_recognition.compare_faces([empleado_encoding], encoding)

                if emparejamiento[0]: # Sí se encontró un match en el sistema para el rostro
                    Asistencia.objects.create(
                        empleado=empleado,
                        fecha=data.get('fecha'),
                        hora_entrada=data.get('hora_entrada'),
                        hora_salida=None
                    )

                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                        pil_image = Image.fromarray(imagen)
                        pil_image.save(temp_image.name)
                        emociones = analyze_emotion(temp_image.name) # Analizar la imagen
                    return Response({'success': f'Asistencia registrada correctamente', 'empleado': empleado.nombre,'emociones': emociones }, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MarcarSalidaAPIView(APIView):
    """
    Vista que permite marcar salida por medio del rostro del empleado

    - Recibe una solictud POST con los datos de salida y el rostro del empleado
    - Carga la imagen a un formato válido para la libreria face_recognition
    - Extrae el encoding facial del rostro entrante
    - Busca si hay un empleado con el cual el encoding haga match
    - Si hay match, guarda la salida del empleado correspondiente en el sistema

    Args:
        request: La solicitud HTTP que contiene los datos de salida y la foto
    Returns:
        JsonResponse: Respuesta en formato JSON con el estado de la operación.
    """
    def put(self, request, *args, **kwargs):
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

            empleados = Empleado.objects.all()
            for empleado in empleados:
                empleado_encoding = empleado.get_caracteristicas_faciales()
                emparejamiento = face_recognition.compare_faces([empleado_encoding], encoding)

                if emparejamiento[0]: # se encuentra coincidencia del rostro
                    asistencia = Asistencia.objects.filter(empleado=empleado, hora_salida=None).last()
                    if asistencia:
                        asistencia.hora_salida = data.get('hora_salida')
                        asistencia.save()
                        return Response({'success': f'Salida registrada correctamente', 'empleado': empleado.nombre}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'No se encontró un registro de entrada activo'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'error': 'Empleado no encontrado o rostro no coincide'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegistrarEmocionAPIView(APIView):
    def post(self, request, asistencia_id, *args, **kwargs):
        pass