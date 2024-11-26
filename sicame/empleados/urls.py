from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistrarEmpleadoAPIView, MarcarAsistenciaAPIView, MarcarSalidaAPIView, RegistrarEmocionAPIView

router = DefaultRouter()

urlpatterns = [
    path('registro', RegistrarEmpleadoAPIView.as_view(), name='registro-empleado'),
    path('marcar-asistencia', MarcarAsistenciaAPIView.as_view(), name='marcar-asistencia'),
    path('marcar-salida', MarcarSalidaAPIView.as_view(), name='marcar-salida'),
    #path('registrar-emocion/<int:asistencia_id>/', RegistrarEmocionAPIView.as_view(), name='registrar-emocion'),
]
