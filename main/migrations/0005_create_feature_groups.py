from django.db import migrations


def create_feature_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for group_name in [
        "blog access",
        "health access",
        "notes access",
        "feeds access",
        "gratitudes access",
    ]:
        Group.objects.get_or_create(name=group_name)


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_privacypolicy"),
    ]

    operations = [
        migrations.RunPython(create_feature_groups, migrations.RunPython.noop),
    ]
