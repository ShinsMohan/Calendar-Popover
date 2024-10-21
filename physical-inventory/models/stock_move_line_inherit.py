from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    adjustment_reason = fields.Text(string='Adjustment Reason')
