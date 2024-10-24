from odoo import api, models

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def _action_done(self):
        res = super()._action_done()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Provide Adjustment Reason',
            'res_model': 'adjustment.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            # 'view_id': self.id,
            'context': {'active_id': self.id},
        }