# Generated by Django 3.2.12 on 2022-03-08 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0003_alter_variavel_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='variavel',
            options={'verbose_name': 'Variavel', 'verbose_name_plural': 'Variaveis'},
        ),
        migrations.AlterField(
            model_name='produto',
            name='preco_marketing',
            field=models.FloatField(verbose_name='Preço'),
        ),
        migrations.AlterField(
            model_name='produto',
            name='promocao_marcketing',
            field=models.FloatField(default=0, verbose_name='Preço Promocional'),
        ),
        migrations.AlterField(
            model_name='produto',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='variavel',
            name='nome',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='variavel',
            name='produto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='produto.produto'),
        ),
    ]