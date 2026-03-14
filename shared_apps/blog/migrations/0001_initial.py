from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title_en', models.CharField(max_length=255, verbose_name='Title English')),
                ('title_ru', models.CharField(max_length=255, verbose_name='Title Russian')),
                ('title_hy', models.CharField(max_length=255, verbose_name='Title Armenian')),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'db_table': 'blog_category',
                'ordering': ['title_en'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title_en', models.CharField(max_length=255, verbose_name='Title English')),
                ('title_ru', models.CharField(max_length=255, verbose_name='Title Russian')),
                ('title_hy', models.CharField(max_length=255, verbose_name='Title Armenian')),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'db_table': 'blog_tag',
                'ordering': ['title_en'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title_en', models.CharField(max_length=255, verbose_name='Title English')),
                ('title_ru', models.CharField(max_length=255, verbose_name='Title Russian')),
                ('title_hy', models.CharField(max_length=255, verbose_name='Title Armenian')),
                ('slug', models.SlugField(unique=True)),
                ('excerpt_en', models.TextField(blank=True, verbose_name='Excerpt English')),
                ('excerpt_ru', models.TextField(blank=True, verbose_name='Excerpt Russian')),
                ('excerpt_hy', models.TextField(blank=True, verbose_name='Excerpt Armenian')),
                ('body_en', models.TextField(verbose_name='Body English')),
                ('body_ru', models.TextField(verbose_name='Body Russian')),
                ('body_hy', models.TextField(verbose_name='Body Armenian')),
                ('cover', models.ImageField(blank=True, null=True, upload_to='blog/covers/')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='draft', max_length=20)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='blog.category')),
                ('tags', models.ManyToManyField(blank=True, related_name='posts', to='blog.tag')),
            ],
            options={
                'db_table': 'blog_post',
                'ordering': ['-published_at', '-id'],
            },
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['status', 'published_at'], name='blog_post_status_b23d34_idx'),
        ),
    ]
