# Generated by Django 3.2.12 on 2022-03-04 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Variavel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('produto', models.CharField(blank=True, max_length=50, null=True)),
                ('preco', models.FloatField()),
                ('preco_promocional', models.FloatField(default=0)),
                ('estoque', models.PositiveIntegerField(default=1)),
                ('nome', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='produto.produto')),
            ],
        ),
    ]
