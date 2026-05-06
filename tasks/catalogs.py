DEFAULT_AREA_SPECS = [
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

DEFAULT_AREA_NAMES = [name for name, _floor, _kind in DEFAULT_AREA_SPECS]

AREA_STATUS_CHOICES = [
    ("Libre", "Libre"),
    ("Ocupado", "Ocupado"),
    ("En mantenimiento", "En mantenimiento"),
]

MAINTENANCE_RESPONSIBLE_CHOICES = [
    ("Mayaj", "Mayaj"),
    ("Osel", "Osel"),
    ("Contabilidad", "Contabilidad"),
    ("Limpieza", "Limpieza"),
    ("Otro", "Otro"),
]

MAINTENANCE_TOPIC_CHOICES = [
    ("Hidraulico", "Hidraulico"),
    ("Electrico", "Electrico"),
    ("Gas", "Gas"),
    ("Limpieza", "Limpieza"),
    ("Mantenimiento", "Mantenimiento"),
    ("Administrativo", "Administrativo"),
    ("Inquilinos", "Inquilinos"),
    ("Morosos", "Morosos"),
    ("Reglamento", "Reglamento"),
    ("Legal", "Legal"),
    ("Otro", "Otro"),
]


def ensure_default_areas(user=None):
    from .models import Area

    for name, floor, kind in DEFAULT_AREA_SPECS:
        area, created = Area.objects.get_or_create(
            nombre=name,
            defaults={
                "numero_piso": floor,
                "tipo_area": kind,
                "estado": "Libre",
                "ubicacion": "BOSS8025",
                "user": user,
            },
        )
        updates = []
        if area.numero_piso != floor:
            area.numero_piso = floor
            updates.append("numero_piso")
        if area.tipo_area != kind:
            area.tipo_area = kind
            updates.append("tipo_area")
        if area.ubicacion != "BOSS8025":
            area.ubicacion = "BOSS8025"
            updates.append("ubicacion")
        if not area.estado:
            area.estado = "Libre"
            updates.append("estado")
        if created is False and user and area.user_id is None:
            area.user = user
            updates.append("user")
        if updates:
            area.save(update_fields=updates)
