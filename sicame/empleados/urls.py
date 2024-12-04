from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VerEmocionesViewSet, RegistrarEmpleadoAPIView, MarcarAsistenciaAPIView, MarcarSalidaAPIView, ActualizarObservacionesAPIView, GenerarReporteAPIView

router = DefaultRouter()
router.register(r"reportes", VerEmocionesViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('registro', RegistrarEmpleadoAPIView.as_view(), name='registro-empleado'),
    path('marcar-asistencia', MarcarAsistenciaAPIView.as_view(), name='marcar-asistencia'),
    path('marcar-salida', MarcarSalidaAPIView.as_view(), name='marcar-salida'),
    path('emocion/<int:emocion_id>/actualizar_observaciones/', ActualizarObservacionesAPIView.as_view(), name='actualizar_observaciones'),
    path('generar-reporte', GenerarReporteAPIView.as_view(), name='generar-reporte'),
]