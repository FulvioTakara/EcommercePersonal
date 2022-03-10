from django.contrib import admin
from .models import Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['idade', 'data_nascimento', 'cpf',
                    'endereco', 'numero', 'complemento', 'bairro', 'cep', 'cidade', 'estado']


