from odoo import models, fields, api

class AdjustmentReasonWizard(models.TransientModel):
    _name = 'adjustment.reason.wizard'
    _description = 'Adjustment Reason Wizard'

    reason = fields.Text(string='Reason', required=True)

    def confirm_reason(self):
        quant = self.env['stock.quant'].browse(self.env.context.get('active_id'))
        move_lines = quant.inventory_quantity_set_ids.mapped('move_line_id')
        for line in move_lines:
            line.adjustment_reason = self.reason

