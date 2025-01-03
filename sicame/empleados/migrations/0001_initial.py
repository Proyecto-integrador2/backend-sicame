# Generated by Django 5.1.3 on 2024-11-25 19:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asistencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True)),
                ('hora_entrada', models.TimeField(blank=True, null=True)),
                ('hora_salida', models.TimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('empleado_id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=254, unique=True)),
                ('cargo', models.CharField(max_length=100)),
                ('caracteristicas_faciales', models.BinaryField()),
            ],
        ),
        migrations.CreateModel(
            name='Emocion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emocion_registrada', models.CharField(max_length=50)),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('asistencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emociones', to='empleados.asistencia')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emociones', to='empleados.empleado')),
            ],
        ),
        migrations.AddField(
            model_name='asistencia',
            name='empleado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asistencias', to='empleados.empleado'),
        ),
    ]
