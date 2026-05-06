from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from tasks.catalogs import DEFAULT_AREA_SPECS
from tasks.models import Area


class Command(BaseCommand):
    help = 'Carga o actualiza las areas base de BOSS8025.'

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        created = 0
        updated = 0

        for nombre, piso, tipo in DEFAULT_AREA_SPECS:
            area, was_created = Area.objects.get_or_create(
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
                area.numero_piso = piso
                area.tipo_area = tipo
                area.ubicacion = 'BOSS8025'
                update_fields = ['numero_piso', 'tipo_area', 'ubicacion']
                if not area.estado:
                    area.estado = 'Libre'
                    update_fields.append('estado')
                if area.user_id is None:
                    area.user = user
                    update_fields.append('user')
                area.save(update_fields=update_fields)
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Areas BOSS8025 listas. Creadas: {created}. Actualizadas: {updated}.'
        ))
