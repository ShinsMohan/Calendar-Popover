from odoo import models, api

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def action_apply_inventory(self):
        res = super(StockQuant,self).action_apply_inventory
        move_line = self.env['stock.move.line'].search([('quant_id', '=', self.id)], limit=1)
    
        if not move_line:
            raise ValueError("No stock move line found for this quant.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Provide Adjustment Reason',
            'res_model': 'adjustment.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_move_line_id': move_line.id},
        }