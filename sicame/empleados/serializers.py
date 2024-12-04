from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Empleado, Asistencia, Emocion

class EmpleadoSerializer(ModelSerializer):
    class Meta:
        model = Empleado
        fields = ["empleado_id", "nombre"]

class AsistenciaSerializer(ModelSerializer):
    class Meta:
        model = Asistencia
        fields = ["fecha", "hora_entrada", "hora_salida"]

class EmocionSerializer(ModelSerializer):
    empleado = EmpleadoSerializer(many=False)
    asistencia = AsistenciaSerializer(many=False)

    class Meta:
        model = Emocion
        fields = ["nombre", "empleado_id", "fecha", "hora_entrada", "hora_salida", "emocion_registrada", "observaciones"]

    def create(self, validated_data):
        empleado_data = validated_data.pop("empleado")
        asistencia_data = validated_data.pop("asistencia")

        # Get Empleado object
        empleado, created = Empleado.objects.get_or_create(**empleado_data)

        # Get Asistencia objects
        asistencia, created = Empleado.objects.get_or_create(**asistencia_data)

        # Create Emocion object
        emocion = Emocion.objects.create(empleado=empleado, asistencia=asistencia, **validated_data)

        return emocion

class GestionEmpleadoSerializer(ModelSerializer):
    ultima_emocion = serializers.SerializerMethodField()

    class Meta:
        model = Empleado
        fields = ['empleado_id', 'nombre', 'cargo', 'ultima_emocion']

    def get_ultima_emocion(self, obj):
        ultima_emocion = Emocion.objects.filter(empleado=obj).order_by('-fecha_hora').first()
        return ultima_emocion.emocion_registrada if ultima_emocion else ''