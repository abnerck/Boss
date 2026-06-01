from django.db import migrations


OLD_NAME = "Porton electrico"
PREFERRED_NAME = "Porton Électrico"


def normalize_porton_electrico(apps, schema_editor):
    Area = apps.get_model("tasks", "Area")
    Mantenimientos = apps.get_model("tasks", "Mantenimientos")

    old_area = Area.objects.filter(nombre=OLD_NAME).first()
    preferred_area = Area.objects.filter(nombre=PREFERRED_NAME).first()

    if old_area and preferred_area:
        Mantenimientos.objects.filter(ubicacion=old_area).update(ubicacion=preferred_area)
        old_area.delete()
        return

    if old_area and not preferred_area:
        old_area.nombre = PREFERRED_NAME
        old_area.save(update_fields=["nombre"])


def restore_porton_electrico(apps, schema_editor):
    Area = apps.get_model("tasks", "Area")
    preferred_area = Area.objects.filter(nombre=PREFERRED_NAME).first()
    if preferred_area and not Area.objects.filter(nombre=OLD_NAME).exists():
        preferred_area.nombre = OLD_NAME
        preferred_area.save(update_fields=["nombre"])


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0007_alter_finanza_categoria"),
    ]

    operations = [
        migrations.RunPython(normalize_porton_electrico, restore_porton_electrico),
    ]
