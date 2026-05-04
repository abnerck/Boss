from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from tasks.models import Area


BOSS8025_AREAS = [
    ('Departamentos', None, 'Departamento'),
    ('Lobby', 0, 'Lobby'),
    ('Estacionamiento', 0, 'Estacionamiento'),
    ('Bombas', 0, 'Cuarto de maquinas'),
    ('Bodega Limpieza', 0, 'Bodega'),
    ('Bodega chica', 0, 'Bodega'),
    ('Bodega 1', 0, 'Bodega'),
    ('Escaleras Lobby', 0, 'Escaleras'),
    ('Pasillo piso 1', 1, 'Pasillo'),
    ('Patio primer piso', 1, 'Area Comun'),
    ('Cuarto de maquinas 1 primer piso', 1, 'Cuarto de maquinas'),
    ('Cuarto de maquinas 2 primer piso', 1, 'Cuarto de maquinas'),
    ('Escaleras Piso 1', 1, 'Escaleras'),
    ('Pasillo piso 2', 2, 'Pasillo'),
    ('Cuarto de maquinas 1 segundo piso', 2, 'Cuarto de maquinas'),
    ('Cuarto de maquinas 2 segundo piso', 2, 'Cuarto de maquinas'),
    ('Escaleras Piso 2', 2, 'Escaleras'),
    ('Pasillo tercer piso', 3, 'Pasillo'),
    ('Cuarto de maquinas 1 tercer piso', 3, 'Cuarto de maquinas'),
    ('Cuarto de maquinas 2 tercer piso', 3, 'Cuarto de maquinas'),
    ('Escaleras Piso 3', 3, 'Escaleras'),
    ('Tinacos/Gas', 4, 'Area Comun'),
    ('Asador', 4, 'Area Comun'),
    ('Sala', 4, 'Area Comun'),
    ('Gym', 4, 'Area Comun'),
    ('Alberca', 4, 'Area Comun'),
    ('Oficina', 0, 'Oficina'),
    ('Azotea roof top', 4, 'Roof top'),
    ('Banos roof top', 4, 'Roof top'),
    ('Cuarto de maquinas roof top', 4, 'Cuarto de maquinas'),
    ('Tinacos roof top', 4, 'Roof top'),
]


class Command(BaseCommand):
    help = 'Carga o actualiza las areas base de BOSS8025.'

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        created = 0
        updated = 0

        for nombre, piso, tipo in BOSS8025_AREAS:
            area, was_created = Area.objects.update_or_create(
                nombre=nombre,
                defaults={
                    'numero_piso': piso,
                    'tipo_area': tipo,
                    'estado': 'Libre',
                    'ubicacion': 'BOSS8025',
                    'user': user,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Areas BOSS8025 listas. Creadas: {created}. Actualizadas: {updated}.'
        ))
