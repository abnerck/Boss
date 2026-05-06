from django.db import migrations, models


def seed_default_areas(apps, schema_editor):
    Area = apps.get_model('tasks', 'Area')
    default_area_specs = [
        ("101", 1, "Departamento"),
        ("102", 1, "Departamento"),
        ("103", 1, "Departamento"),
        ("104", 1, "Departamento"),
        ("105", 1, "Departamento"),
        ("106", 1, "Departamento"),
        ("107", 1, "Departamento"),
        ("201", 2, "Departamento"),
        ("202", 2, "Departamento"),
        ("203", 2, "Departamento"),
        ("204", 2, "Departamento"),
        ("205", 2, "Departamento"),
        ("206", 2, "Departamento"),
        ("207", 2, "Departamento"),
        ("301", 3, "Departamento"),
        ("302", 3, "Departamento"),
        ("303", 3, "Departamento"),
        ("304", 3, "Departamento"),
        ("305", 3, "Departamento"),
        ("306", 3, "Departamento"),
        ("Lobby", 0, "Area comun"),
        ("Elevador", 0, "Area comun"),
        ("Estacionamiento", 0, "Area comun"),
        ("Porton electrico", 0, "Area comun"),
        ("Cisterna", 0, "Cuarto de maquinas"),
        ("Bombas de subida", 0, "Cuarto de maquinas"),
        ("Bodega de limpieza", 0, "Bodega"),
        ("Bodega chica", 0, "Bodega"),
        ("Bodega 1", 0, "Bodega"),
        ("Escaleras", 0, "Escaleras"),
        ("Pasillo piso 1", 1, "Pasillo"),
        ("Patio primer piso", 1, "Area comun"),
        ("Cuarto de maquinas 1 primer piso", 1, "Cuarto de maquinas"),
        ("Cuarto de maquinas 2 primer piso", 1, "Cuarto de maquinas"),
        ("Escaleras Piso 1", 1, "Escaleras"),
        ("Pasillo piso 2", 2, "Pasillo"),
        ("Cuarto de maquinas 1 segundo piso", 2, "Cuarto de maquinas"),
        ("Cuarto de maquinas 2 segundo piso", 2, "Cuarto de maquinas"),
        ("Escaleras Piso 2", 2, "Escaleras"),
        ("Pasillo tercer piso", 3, "Pasillo"),
        ("Cuarto de maquinas 1 tercer piso", 3, "Cuarto de maquinas"),
        ("Cuarto de maquinas 2 tercer piso", 3, "Cuarto de maquinas"),
        ("Escaleras Piso 3", 3, "Escaleras"),
        ("Tinacos/Gas", 4, "Roof top"),
        ("Asador", 4, "Roof top"),
        ("Sala", 4, "Roof top"),
        ("Gym", 4, "Roof top"),
        ("Alberca", 4, "Roof top"),
        ("Oficina", 0, "Oficina"),
        ("Azotea roof top", 4, "Roof top"),
        ("Banos roof top", 4, "Roof top"),
        ("Cuarto de maquinas roof top", 4, "Cuarto de maquinas"),
        ("Tinacos roof top", 4, "Roof top"),
    ]
    for nombre, piso, tipo in default_area_specs:
        area, created = Area.objects.get_or_create(
            nombre=nombre,
            defaults={
                'numero_piso': piso,
                'tipo_area': tipo,
                'estado': 'Libre',
                'ubicacion': 'BOSS8025',
            },
        )
        if not created:
            area.numero_piso = piso
            area.tipo_area = tipo
            area.ubicacion = 'BOSS8025'
            update_fields = ['numero_piso', 'tipo_area', 'ubicacion']
            if not area.estado:
                area.estado = 'Libre'
                update_fields.append('estado')
            area.save(update_fields=update_fields)


class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0004_normalize_finanza_totals'),
    ]

    operations = [
        migrations.AddField(
            model_name='mantenimientos',
            name='fecha_inicio',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunPython(seed_default_areas, migrations.RunPython.noop),
    ]
