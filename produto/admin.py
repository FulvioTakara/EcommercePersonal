from django.contrib import admin
from .models import Produto, Variavel
from .forms import VariacaoObrigatoria


class VariacaoInline(admin.TabularInline):
    model = Variavel
    formset = VariacaoObrigatoria
    extra = 0
    min_num = 1
    can_delete = True


class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao_curta', 'get_preco_formatado',
                    'get_preco_promocional_formatado']
    inlines = [
        VariacaoInline
    ]


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Variavel)
