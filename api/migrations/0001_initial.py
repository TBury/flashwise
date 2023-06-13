# Generated by Django 4.2 on 2023-04-17 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('level', models.CharField(choices=[('easy', 'Początkujący'), ('medi', 'Średniozaawansowany'), ('hard', 'Zaawansowany')], max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='FlashcardsSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=96)),
                ('status', models.CharField(choices=[('public', 'Publiczny'), ('private', 'Prywatny')], default='public', max_length=7)),
                ('is_premium', models.BooleanField(default=False)),
                ('slug', models.SlugField(default=models.CharField(max_length=96))),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.PositiveSmallIntegerField()),
                ('set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.flashcardsset')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_created=True, auto_now=True)),
                ('action', models.CharField(choices=[('A1', 'Użytkownik zalogował się do systemu.'), ('A2', 'Użytkownik wylogował się z systemu.'), ('B1', 'Utworzono fiszkę.'), ('B2', 'Utworzono zestaw.')], max_length=2)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.user')),
            ],
        ),
        migrations.AddField(
            model_name='flashcardsset',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.user'),
        ),
        migrations.AddField(
            model_name='flashcardsset',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.category'),
        ),
        migrations.AddField(
            model_name='flashcardsset',
            name='tag',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.tag'),
        ),
        migrations.CreateModel(
            name='Flashcard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('front', models.TextField()),
                ('back', models.TextField()),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.user')),
                ('flashcard_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.flashcardsset')),
            ],
        ),
    ]