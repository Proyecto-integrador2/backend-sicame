from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse
from .models import Empleado, Asistencia, Emocion
import face_recognition
from google.cloud import vision

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

            empleados = Empleado.objects.all()
            for empleado in empleados:
                empleado_encoding = empleado.get_caracteristicas_faciales()
                emparejamiento = face_recognition.compare_faces([empleado_encoding], encoding)

                if emparejamiento[0]: # Sí se encontró un match en el sistema para el rostro
                    asistencia = Asistencia.objects.create(
                        empleado=empleado,
                        fecha=data.get('fecha'),
                        hora_entrada=data.get('hora_entrada'),
                        hora_salida=None
                    )

                    # se registra la emocion de entrada
                    resultado = registrar_emocion(asistencia, request.FILES.get('foto'))
                    emocion = resultado['emocion']
                    ultimo_registro = resultado['ultimo_registro']
                    return Response({'success': f'Asistencia registrada correctamente', 'empleado': empleado.nombre, 'id': empleado.empleado_id, 'cargo': empleado.cargo, 'emocion': emocion.emocion_registrada, 'id_emocion': emocion.id, 'ultimo_registro': ultimo_registro}, status=status.HTTP_200_OK)
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

                        # se registra la emocion de salida
                        resultado = registrar_emocion(asistencia, request.FILES.get('foto'))
                        emocion = resultado['emocion']
                        ultimo_registro = resultado['ultimo_registro']
                        return Response({'success': f'Salida registrada correctamente',  'empleado': empleado.nombre, 'id': empleado.empleado_id, 'cargo': empleado.cargo, 'emocion': emocion.emocion_registrada, 'id_emocion': emocion.id, 'ultimo_registro': ultimo_registro}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'No se encontró un registro de entrada activo'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'error': 'Empleado no encontrado o rostro no coincide'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def registrar_emocion(asistencia, imagen):
    """
    Usa Google Vision API para analizar la emocion en la imagen y la guarda.

    - Crea un cliente de GV API
    - Lee el rostro e identifica la emocion predominante
    - Guarda la respectiva emoción de entrada y/o salida del empleado

    Args:
        Instancia de asistencia (ya sea para la hora de entrada o de salida) y la imagen
    Returns:
        JsonResponse: Respuesta en formato JSON con el estado de la operación.
    """
    cliente_gcv = vision.ImageAnnotatorClient()
    imagen.seek(0)
    content = imagen.read()
    if not content:
        print('No se pudo leer la imagen')

    image = vision.Image(content=content)

    respuesta = cliente_gcv.face_detection(image=image)
    caras = respuesta.face_annotations

    if not caras:
        return JsonResponse({'error': 'No se detectó ningún rostro'}, status=status.HTTP_400_BAD_REQUEST)

    cara = caras[0]
    emociones = {
        "Alegría": cara.joy_likelihood,
        "Tristeza": cara.sorrow_likelihood,
        "Enojo": cara.anger_likelihood,
        "Sorpresa": cara.surprise_likelihood,
    }

    if len(set(emociones.values())) == 1:
        emocion = "Neutral"
    else:
        emocion = max(emociones, key=emociones.get)

    emocion_instance = Emocion.objects.create(
        empleado=asistencia.empleado,
        asistencia=asistencia,
        emocion_registrada=emocion
    )
    ultimo_registro = Asistencia.objects.filter(empleado=asistencia.empleado).order_by('-fecha', '-hora_entrada').first()

    return {
        'ultimo_registro': {
            'fecha': ultimo_registro.fecha,
            'hora_entrada': ultimo_registro.hora_entrada,
            'hora_salida': ultimo_registro.hora_salida,
        },
        'emocion': emocion_instance,
    }

class ActualizarObservacionesAPIView(APIView):
    """
    Vista para actualizar el campo observaciones de una instancia de Emocion.

    - Recibe una solicitud PATCH con las nuevas observaciones
    - Actualiza el campo observaciones de la instancia de Emocion especificada

    Args:
        request: La solicitud HTTP que contiene las nuevas observaciones
        emocion_id: El ID de la instancia de Emocion a actualizar
    Returns:
        JsonResponse: Respuesta en formato JSON con el estado de la operación.
    """
    def patch(self, request, emocion_id, *args, **kwargs):
        try:
            emocion = Emocion.objects.get(id=emocion_id)
        except Emocion.DoesNotExist:
            return Response({'error': 'Emocion no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        observaciones = request.data.get('observaciones')
        if observaciones is not None:
            emocion.observaciones = observaciones
            emocion.save()
            return Response({'message': 'Observaciones actualizadas correctamente'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'El campo observaciones es requerido'}, status=status.HTTP_400_BAD_REQUEST)    