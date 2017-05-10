# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Gabriel Cardoso de Faria<gabriel.cardoso@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class GarantiaContrato(models.Model):
    _name = 'garantia.contrato'

    proporcao_total = fields.Float(
        string=u'Porcentagem do valor do contrato',
        digits=(3, 2)
    )

    valor_total = fields.Float(
        string=u'Valor total da garantia',
        digits=(16, 2)
    )

    prazo_dias = fields.Integer(
        string=u'Prazo em dias para apresentar a garantia'
    )

    prorrogado = fields.Boolean(
        string=u'O prazo foi prorrogado?'
    )

    prorrogado_dias = fields.Integer(
        string=u'Em quantos dias?'
    )

    situacao = fields.Selection(
        selection=[
            ('entregue', 'Entregue'),
            ('pendente', 'Pendente'),
            ('atraso', 'Em atraso')
        ],
        default='pendente',
        string=u'Situação:'
    )

    entregue_em = fields.Date(
        string=u'em '
    )

    seguradora = fields.Char(
        string=u'Seguradora'
    )

    modalidade = fields.Char(
        string=u'Modalidade'
    )

    vigencia_inicio = fields.Date(
        string=u'Vigência de:'
    )

    vigencia_fim = fields.Date(
        string=u'até:'
    )

    garantia_digital = fields.Binary(
        string=u'Visualizar Garantia Digitalizada',
    )

    nome_arquivo_garantia = fields.Char(
        string=u'Nome do arquivo'
    )

    contrato_id = fields.Many2one(
        comodel_name='account.analytic.account',
        inverse_name='garantia_contrato_ids',
        ondelete='cascade',
        required='True'
    )

    @api.onchange('nome_arquivo_garantia')
    def _verifica_nome_arquivo(self):
        for garantia in self:
            if not garantia.garantia_digital:
                continue
            if not garantia.nome_arquivo_garantia:
                raise ValidationError(_("Nome do arquivo não encontrado"))
            elif garantia.nome_arquivo_garantia.split('.')[-1] != 'pdf':
                garantia.write({'garantia_digital': False})
                raise ValidationError(_("O arquivo digital deve estar em "
                                        "formado PDF"))
