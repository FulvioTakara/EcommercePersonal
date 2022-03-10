from django.shortcuts import redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.contrib import messages

from produto.models import Variavel
from .models import Pedido, ItemPedido

from EcommercePersonal.utils import utils


class DispatchLoginRequiredMixin(View):
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authyenticated:
            return redirect('perfil:criar')

        return super().dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(usuario=self.request.user)
        return qs


class Pagar(DispatchLoginRequiredMixin, DetailView):
    template_name = 'pedido/pagar.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'


class SalvarPedido(View):
    template_name = 'pedido/pagar.html'

    def get(self, *args, **kwargs):
        if not self.request.user.is_authyenticated:
            messages.error(
                self.request, 'Você precisa fazer o login.'
            )
            return redirect('perfil:criar')

        if not self.request.sessiom.get('carrinho'):
            messages.error(
                self.request, 'Seu carrinho está vazio.'
            )
            return redirect('produto:lista')

        carrinho = self.request.session.get('carrinho')
        carrinho_variacao_ids = [v for v in carrinho]
        bd_varicoes = list(
            Variavel.objects.select_related('produto').filter(
                id_in=carrinho_variacao_ids
            )
        )

        for variavel in bd_varicoes:
            vid = str(variavel.id)

            estoque = variavel.estoque
            qtd_carrinho = carrinho[vid]['quantidade']
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promo = carrinho[vid]['preco_unitario_promocinal']

            error_msg_estoque = ''

            if estoque < qtd_carrinho:
                carrinho[vid]['quantidade'] = estoque
                carrinho[vid]['preco_quantitativo'] = estoque * preco_unt
                carrinho[vid]['preco_quantitativo_promocional'] = \
                    estoque * preco_unt_promo

                error_msg_estoque = 'Estoque insuficiente para alguns produtos de ' \
                                    'seu carrinho. Reduzimos a quantidade desses produtos.' \
                                    'Por favor, verifique quais produtos foram afetados a segir.'

            if error_msg_estoque:
                messages.error(
                    self.request,
                    error_msg_estoque
                )

                self.request.session.save()
                return redirect('produto:carrinho')

            qtd_total_carrinho = utils.cart_total_qtd(carrinho)
            valor_total_carrinho = utils.cart_totals(carrinho)

            pedido = Pedido(
                usuario=self.request.user,
                total=valor_total_carrinho,
                qtd_total=qtd_total_carrinho,
                status='C',
            )

            pedido.save()

            ItemPedido.objects.bulk_create(
                [
                    ItemPedido(
                        pedido=pedido,
                        produto=v['produto_nome'],
                        produto_id=v['produto_id'],
                        variavel=v['variavel_nome'],
                        variavel_id=v['variavel_id'],
                        preco=v['preco_quantitativo'],
                        preco_promocional=v['preco_quantitativo_promocional'],
                        quantidade=v['quantidade'],
                        imagem=v['imagem'],
                    ) for v in carrinho.values()
                ]
            )

            del self.request.session['carrinho']

            return redirect(
                reverse(
                    'pedido:pagar',
                    kwargs={
                        'pk': pedido.pk
                    }
                )
            )


class Detalhe(DispatchLoginRequiredMixin, DetailView):
    model = Pedido
    context_object_name = 'pedido'
    template_name = 'pedido/detalhe.html'
    pk_url_kwarg = 'pk'


class Lista(DispatchLoginRequiredMixin, ListView):
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedido/lista.html'
    paginate_by = 10
    odering = ['-id']
