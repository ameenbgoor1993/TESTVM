import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.models import Area

# Fetch all areas
areas = Area.objects.all().order_by('id')
count = areas.count()

print(f"Found {count} existing areas.")

if count == 0:
    print("No areas found. Creating 5 dummy areas.")
    for i in range(1, 6):
        Area.objects.create(
            name_en=f"Area {i}",
            name_ar=f"المنطقة {i}",
            description=f"Description for Area {i}"
        )
    print("Created 5 areas.")
else:
    for i, area in enumerate(areas, 1):
        area.name_en = f"Area {i}"
        area.name_ar = f"المنطقة {i}"
        area.save()
        print(f"Updated Area ID {area.id} to '{area.name_en}' / '{area.name_ar}'")

    print("All areas updated.")
