from rest_framework.serializers import ModelSerializer
from .models import Empleado, Asistencia, Emocion


class EmpleadoSerializer(ModelSerializer):
    class Meta:
        model = Empleado
        fields = ("empleado_id", "nombre")


class AsistenciaSerializer(ModelSerializer):
    class Meta:
        model = Asistencia
        fields = ("fecha", "hora_entrada", "hora_salida")


class EmocionSerializer(ModelSerializer):
    empleado = EmpleadoSerializer(many=False)
    asistencia = AsistenciaSerializer(many=False)

    class Meta:
        model = Emocion
        fields = (
            "empleado",
            "asistencia",
            "emocion_registrada",
            "fecha_hora",
            "observaciones",
        )

    def create(self, validated_data):
        empleado_data = validated_data.pop("empleado")
        asistencia_data = validated_data.pop("asistencia")

        # Get Empleado object
        empleado, created = Empleado.objects.get_or_create(**empleado_data)

        # Get Asistencia objects
        asistencia, created = Empleado.objects.get_or_create(**asistencia_data)

        # Create Emocion object
        emocion = Emocion.objects.create(
            empleado=empleado, asistencia=asistencia, **validated_data
        )

        return emocion
