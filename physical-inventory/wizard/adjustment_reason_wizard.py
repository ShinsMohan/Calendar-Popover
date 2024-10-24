from odoo import models, fields

class AdjustmentReasonWizard(models.TransientModel):
    _name = 'adjustment.reason.wizard'
    _description = 'Adjustment Reason Wizard'

    reason = fields.Text(string='Adjustment Reason', required=True)

    def confirm_reason(self):
        move_line_id = self.env.context.get('active_move_line_id')
        if not move_line_id:
            raise ValueError("No active move line ID found in context.")
        move_line = self.env['stock.move.line'].browse(move_line_id)
        move_line.adjustment_reason = self.reason
        return {'type': 'ir.actions.act_window_close'}