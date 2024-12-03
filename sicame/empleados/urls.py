from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistrarEmpleadoAPIView, MarcarAsistenciaAPIView, MarcarSalidaAPIView, ActualizarObservacionesAPIView

router = DefaultRouter()

urlpatterns = [
    path('registro', RegistrarEmpleadoAPIView.as_view(), name='registro-empleado'),
    path('marcar-asistencia', MarcarAsistenciaAPIView.as_view(), name='marcar-asistencia'),
    path('marcar-salida', MarcarSalidaAPIView.as_view(), name='marcar-salida'),
    path('emocion/<int:emocion_id>/actualizar_observaciones/', ActualizarObservacionesAPIView.as_view(), name='actualizar_observaciones'),
]