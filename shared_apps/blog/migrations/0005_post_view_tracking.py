from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_post_excerpt_hy'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='view_count_canvas',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='view_count_poem',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='view_count_total',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='view_count_yatuk',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='PostView',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('device_id', models.CharField(max_length=64)),
                ('viewed_date', models.DateField()),
                (
                    'domain',
                    models.CharField(
                        choices=[
                            ('yatuk', 'yatuk.am'),
                            ('yatukpoem', 'poem.yatuk.am'),
                            ('yatukcanvas', 'canvas.yatuk.am'),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    'post',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='views',
                        to='blog.post',
                    ),
                ),
            ],
            options={
                'db_table': 'blog_post_view',
                'ordering': ['-created_at', '-id'],
            },
        ),
        migrations.AddConstraint(
            model_name='postview',
            constraint=models.UniqueConstraint(
                fields=('post', 'device_id', 'viewed_date', 'domain'),
                name='uniq_blog_view_post_device_day_domain',
            ),
        ),
        migrations.AddIndex(
            model_name='postview',
            index=models.Index(
                fields=['post', 'domain'],
                name='blog_post_vi_post_id_89c828_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='postview',
            index=models.Index(
                fields=['viewed_date'],
                name='blog_post_vi_viewed__d54536_idx',
            ),
        ),
    ]
