from django.contrib import admin
from .models import Produto, Variavel


class VariacaoInline(admin.TabularInline):
    model = Variavel
    extra = 1


class ProdutoAdmin(admin.ModelAdmin):
    inlines = [
        VariacaoInline
    ]


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Variavel)
