from odoo import models, api

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def _action_done(self):
        # Call the original action_done method
        res = super(StockInventory, self)._action_done()

        # Return the wizard action after the original action completes
        return {
            'type': 'ir.actions.act_window',
            'name': 'Provide Adjustment Reason',
            'res_model': 'adjustment.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }
