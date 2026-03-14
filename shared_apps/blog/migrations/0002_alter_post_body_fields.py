import django.db.models
from django.db import migrations

try:
    from tinymce.models import HTMLField
except ImportError:
    HTMLField = django.db.models.TextField


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='body_en',
            field=HTMLField(verbose_name='Body English'),
        ),
        migrations.AlterField(
            model_name='post',
            name='body_ru',
            field=HTMLField(verbose_name='Body Russian'),
        ),
        migrations.AlterField(
            model_name='post',
            name='body_hy',
            field=HTMLField(verbose_name='Body Armenian'),
        ),
    ]
