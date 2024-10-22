from odoo import models, api

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def action_apply_inventory(self):
        res = super(StockQuant, self).action_apply_inventory()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Provide Adjustment Reason',
            'res_model': 'adjustment.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }
