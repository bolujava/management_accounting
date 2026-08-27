# # If Mr Omooba/Fintrak does not need actual detach the model from here
# from odoo import models, fields, api
#
# class MngtSbuActualRow(models.Model):
#     _name = 'mngt.sbu.actual.row'
#     _description = 'Actuals Input (Account Manager Only)'
#     _order = 'sequence'
#
#     sbu_id = fields.Many2one('mngt.sbu', string='SBU', ondelete='cascade')
#     sequence = fields.Integer(string='Seq', default=10)
#     row_name = fields.Char(string='SOCI Item')
#
#     actual_m1 = fields.Float(string='Actual Jan')
#     actual_m2 = fields.Float(string='Actual Feb')
#     actual_m3 = fields.Float(string='Actual Mar')
#     actual_m4 = fields.Float(string='Actual Apr')
#     actual_m5 = fields.Float(string='Actual May')
#     actual_m6 = fields.Float(string='Actual Jun')
#     actual_m7 = fields.Float(string='Actual Jul')
#     actual_m8 = fields.Float(string='Actual Aug')
#     actual_m9 = fields.Float(string='Actual Sep')
#     actual_m10 = fields.Float(string='Actual Oct')
#     actual_m11 = fields.Float(string='Actual Nov')
#     actual_m12 = fields.Float(string='Actual Dec')
#     # Remove if achievement is not needed
#     achievement_m1 = fields.Float(compute='_compute_achievement', string='Ach % Jan')
#     achievement_m2 = fields.Float(compute='_compute_achievement', string='Ach % Feb')
#     achievement_m3 = fields.Float(compute='_compute_achievement', string='Ach % Mar')
#     achievement_m4 = fields.Float(compute='_compute_achievement', string='Ach % Apr')
#     achievement_m5 = fields.Float(compute='_compute_achievement', string='Ach % May')
#     achievement_m6 = fields.Float(compute='_compute_achievement', string='Ach % Jun')
#     achievement_m7 = fields.Float(compute='_compute_achievement', string='Ach % Jul')
#     achievement_m8 = fields.Float(compute='_compute_achievement', string='Ach % Aug')
#     achievement_m9 = fields.Float(compute='_compute_achievement', string='Ach % Sep')
#     achievement_m10 = fields.Float(compute='_compute_achievement', string='Ach % Oct')
#     achievement_m11 = fields.Float(compute='_compute_achievement', string='Ach % Nov')
#     achievement_m12 = fields.Float(compute='_compute_achievement', string='Ach % Dec')
#
#     actual_total = fields.Float(compute='_compute_actual_total', string='Actual Total')
#
#     @api.depends('actual_m1', 'actual_m2', 'actual_m3', 'actual_m4', 'actual_m5', 'actual_m6',
#                  'actual_m7', 'actual_m8', 'actual_m9', 'actual_m10', 'actual_m11', 'actual_m12')
#     def _compute_actual_total(self):
#         for rec in self:
#             rec.actual_total = sum([rec.actual_m1, rec.actual_m2, rec.actual_m3, rec.actual_m4,
#                                     rec.actual_m5, rec.actual_m6, rec.actual_m7, rec.actual_m8,
#                                     rec.actual_m9, rec.actual_m10, rec.actual_m11, rec.actual_m12])
#
#     @api.depends(
#         'actual_m1', 'actual_m2', 'actual_m3', 'actual_m4', 'actual_m5', 'actual_m6',
#         'actual_m7', 'actual_m8', 'actual_m9', 'actual_m10', 'actual_m11', 'actual_m12',
#         'sbu_id.soci_row_ids.m1', 'sbu_id.soci_row_ids.m2', 'sbu_id.soci_row_ids.m3',
#         'sbu_id.soci_row_ids.m4', 'sbu_id.soci_row_ids.m5', 'sbu_id.soci_row_ids.m6',
#         'sbu_id.soci_row_ids.m7', 'sbu_id.soci_row_ids.m8', 'sbu_id.soci_row_ids.m9',
#         'sbu_id.soci_row_ids.m10', 'sbu_id.soci_row_ids.m11', 'sbu_id.soci_row_ids.m12'
#     )
#     def _compute_variance(self):
#         for rec in self:
#             # 1. Find the matching budget row by 'row_name'
#             budget_row = rec.sbu_id.soci_row_ids.filtered(lambda r: r.row_name == rec.row_name)
#             if not budget_row:
#                 # If no matching budget row, variance is just the actual
#                 rec.variance_m1 = rec.actual_m1
#                 rec.variance_m2 = rec.actual_m2
#                 rec.variance_m3 = rec.actual_m3
#                 rec.variance_m4 = rec.actual_m4
#                 rec.variance_m5 = rec.actual_m5
#                 rec.variance_m6 = rec.actual_m6
#                 rec.variance_m7 = rec.actual_m7
#                 rec.variance_m8 = rec.actual_m8
#                 rec.variance_m9 = rec.actual_m9
#                 rec.variance_m10 = rec.actual_m10
#                 rec.variance_m11 = rec.actual_m11
#                 rec.variance_m12 = rec.actual_m12
#                 continue
#
#             # 2. Determine if this is a Revenue or Cost line using row_type
#             is_revenue = budget_row.row_type in ['subtotal', 'net_revenue', 'contribution', 'profit_before_tax',
#                                                  'profit_after_tax']
#
#             if is_revenue:
#                 # Revenue Variance: Actual - Budget
#                 rec.variance_m1 = rec.actual_m1 - budget_row.m1
#                 rec.variance_m2 = rec.actual_m2 - budget_row.m2
#                 rec.variance_m3 = rec.actual_m3 - budget_row.m3
#                 rec.variance_m4 = rec.actual_m4 - budget_row.m4
#                 rec.variance_m5 = rec.actual_m5 - budget_row.m5
#                 rec.variance_m6 = rec.actual_m6 - budget_row.m6
#                 rec.variance_m7 = rec.actual_m7 - budget_row.m7
#                 rec.variance_m8 = rec.actual_m8 - budget_row.m8
#                 rec.variance_m9 = rec.actual_m9 - budget_row.m9
#                 rec.variance_m10 = rec.actual_m10 - budget_row.m10
#                 rec.variance_m11 = rec.actual_m11 - budget_row.m11
#                 rec.variance_m12 = rec.actual_m12 - budget_row.m12
#             else:
#                 # Cost/Expense Variance: Budget - Actual (Positive = Good)
#                 rec.variance_m1 = budget_row.m1 - rec.actual_m1
#                 rec.variance_m2 = budget_row.m2 - rec.actual_m2
#                 rec.variance_m3 = budget_row.m3 - rec.actual_m3
#                 rec.variance_m4 = budget_row.m4 - rec.actual_m4
#                 rec.variance_m5 = budget_row.m5 - rec.actual_m5
#                 rec.variance_m6 = budget_row.m6 - rec.actual_m6
#                 rec.variance_m7 = budget_row.m7 - rec.actual_m7
#                 rec.variance_m8 = budget_row.m8 - rec.actual_m8
#                 rec.variance_m9 = budget_row.m9 - rec.actual_m9
#                 rec.variance_m10 = budget_row.m10 - rec.actual_m10
#                 rec.variance_m11 = budget_row.m11 - rec.actual_m11
#                 rec.variance_m12 = budget_row.m12 - rec.actual_m12
#
#     @api.depends(
#         'actual_m1', 'actual_m2', 'actual_m3', 'actual_m4', 'actual_m5', 'actual_m6',
#         'actual_m7', 'actual_m8', 'actual_m9', 'actual_m10', 'actual_m11', 'actual_m12',
#         'sbu_id.soci_row_ids.m1', 'sbu_id.soci_row_ids.m2', 'sbu_id.soci_row_ids.m3',
#         'sbu_id.soci_row_ids.m4', 'sbu_id.soci_row_ids.m5', 'sbu_id.soci_row_ids.m6',
#         'sbu_id.soci_row_ids.m7', 'sbu_id.soci_row_ids.m8', 'sbu_id.soci_row_ids.m9',
#         'sbu_id.soci_row_ids.m10', 'sbu_id.soci_row_ids.m11', 'sbu_id.soci_row_ids.m12'
#     )
#     def _compute_achievement(self):
#         for rec in self:
#             # Find matching budget row
#             budget_row = rec.sbu_id.soci_row_ids.filtered(lambda r: r.row_name == rec.row_name)
#
#             if not budget_row:
#                 rec.achievement_m1 = 0.0
#                 rec.achievement_m2 = 0.0
#                 rec.achievement_m3 = 0.0
#                 rec.achievement_m4 = 0.0
#                 rec.achievement_m5 = 0.0
#                 rec.achievement_m6 = 0.0
#                 rec.achievement_m7 = 0.0
#                 rec.achievement_m8 = 0.0
#                 rec.achievement_m9 = 0.0
#                 rec.achievement_m10 = 0.0
#                 rec.achievement_m11 = 0.0
#                 rec.achievement_m12 = 0.0
#                 continue
#
#             # Helper function to avoid division by zero
#             def get_pct(actual, budget):
#                 if budget == 0:
#                     return 100.0 if actual == 0 else 0.0
#                 return (actual / budget) * 100
#
#             rec.achievement_m1 = get_pct(rec.actual_m1, budget_row.m1)
#             rec.achievement_m2 = get_pct(rec.actual_m2, budget_row.m2)
#             rec.achievement_m3 = get_pct(rec.actual_m3, budget_row.m3)
#             rec.achievement_m4 = get_pct(rec.actual_m4, budget_row.m4)
#             rec.achievement_m5 = get_pct(rec.actual_m5, budget_row.m5)
#             rec.achievement_m6 = get_pct(rec.actual_m6, budget_row.m6)
#             rec.achievement_m7 = get_pct(rec.actual_m7, budget_row.m7)
#             rec.achievement_m8 = get_pct(rec.actual_m8, budget_row.m8)
#             rec.achievement_m9 = get_pct(rec.actual_m9, budget_row.m9)
#             rec.achievement_m10 = get_pct(rec.actual_m10, budget_row.m10)
#             rec.achievement_m11 = get_pct(rec.actual_m11, budget_row.m11)
#             rec.achievement_m12 = get_pct(rec.actual_m12, budget_row.m12)