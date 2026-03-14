from django.db import migrations
from django.db import models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_post_view_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='share_image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='blog/share/',
                verbose_name=_('Share Image'),
            ),
        ),
    ]
