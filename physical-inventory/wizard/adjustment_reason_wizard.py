from odoo import models, fields

class AdjustmentReasonWizard(models.TransientModel):
    _name = 'adjustment.reason.wizard'
    _description = 'Adjustment Reason Wizard'

    reason = fields.Text(string='Adjustment Reason', required=True)

    def confirm_reason(self):
        inventory = self.env['stock.inventory'].browse(self.env.context.get('active_id'))
        move_lines = inventory.move_ids_without_package.mapped('move_line_ids')
        for line in move_lines:
            line.adjustment_reason = self.reason