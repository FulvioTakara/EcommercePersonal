from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View

from django.contrib import messages
from django.db.models import Q

from .models import Produto, Variavel
from perfil.models import Perfil


class ListaProdutos(ListView):
    model = Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    ordering = ['id']


class Busca(ListaProdutos):
    def get_queryset(self, *args, **kwargs):
        termo = self.request.GET.get('termo') or self.request.session['termo']
        qs = super().get_queryset(*args, **kwargs)

        if not termo:
            return qs

        self.request.session['termo'] = termo

        qs = qs.filter(
            Q(nome_icontains=termo) |
            Q(descricao_curta_icontains=termo) |
            Q(descricao_longa_icontains=termo)
        )

        self.request.session.save()
        return qs


class DetalheProduto(DetailView):
    model = Produto
    template_name = 'produto_detalhe.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'


class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )
        variavel_id = self.request.GET.get('vid')

        if not variavel_id:
            messages.error(
                self.request,
                'Produto não existe'
            )
            return redirect(http_referer)

        variavel = get_object_or_404(Variavel, id=variavel_id)
        variavel_estoque = variavel.estoque
        produto = variavel.produto

        produto_id = produto.id
        produto_nome = produto.nome
        variavel_nome = variavel.nome or ''
        preco_unitario = variavel.preco
        preco_unitario_promocional = variavel.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem

        if imagem:
            imagem = imagem.name
        else:
            imagem = ''

        if variavel.estoque < 1:
            messages.error(
                self.request,
                'Estoque insuficiente'
            )
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save()

        carrinho = self.request.session['carrinho']

        if variavel_id in carrinho:
            quantidade_carrinho = carrinho[variavel_id]['quantidade']
            quantidade_carrinho += 1

            if variavel_estoque < quantidade_carrinho:
                messages.warning(
                    self.request,
                    f'Estoque insuficiente para {quantidade_carrinho}x no '
                    f'produto "{produto_nome}". Adicionamos {variavel_estoque}x em '
                    f'seu carrinho '
                )
                quantidade_carrinho = variavel_estoque

            carrinho[variavel_id]['quantidade'] = quantidade_carrinho
            carrinho[variavel_id]['preco_quantitativo'] = \
                preco_unitario * quantidade_carrinho
            carrinho[variavel_id]['preco_quantitativo_promocional'] = \
                preco_unitario_promocional * quantidade_carrinho
        else:
            carrinho[variavel_id] = {
                'produto_id': produto_id,
                'produto_nome': produto_nome,
                'variavel_nome': variavel_nome,
                'variavel_id': variavel_id,
                'preco_unitario': preco_unitario,
                'preco_unitario_promocional': preco_unitario_promocional,
                'preco_quantitativo': preco_unitario,
                'preco_quantitativo_promocional': preco_unitario_promocional,
                'quantidade': 1,
                'slug': slug,
                'imagem': imagem,
            }

        self.request.session.save()

        messages.success(
            self.request,
            f'{produto_nome} {variavel_nome} adicionado ao seu carrinho '
            f'{carrinho[variavel_id]["quantidade"]}x.'
        )

        return redirect(http_referer)


class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )
        variavel_id = self.request.GET.get('vid')

        if not variavel_id:
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            return redirect(http_referer)

        carrinho = self.request.session['carrinho'][variavel_id]

        messages.success(
            self.request,
            f'{carrinho["produto_nome"]} {carrinho["variavel_nome"]} removido do seu '
            f'carrinho.'
        )

        del self.request.session['carrinho'][variavel_id]
        self.request.session.save()
        return redirect(http_referer)


class Carrinho(View):
    def get(self, *args, **kwargs):
        contexto = {
            'carrinho': self.request.session.get('carrinho', {})
        }

        return render(self.request, 'produto/carrinho.html, contexto')


class ResumoDaCompra(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        perfil = Perfil.objects.filter(usuario=self.request.user).exists()

        if not perfil:
            messages.error(
                self.request,
                'Usuário sem perfil'
            )
            return redirect('perfil:criar')

        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'Carrinho vazio.'
            )
            return redirect('produto:lista')

        contexto = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho'],
        }

        return render(self.request, 'produto/resumodacompra.html', contexto)
