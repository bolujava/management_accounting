import base64
import io
import xlrd  # Make sure to install xlrd (pip install xlrd)
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime


class MngtBudgetPeriod(models.Model):
    _name = 'mngt.budget.period'
    _description = '2026 Consolidated Budget (Image 1)'

    name = fields.Char(string='Period', required=True, default=lambda self: f"{datetime.now().year} Budget")
    year = fields.Char(string='Year', required=True, default=lambda self: str(datetime.now().year))

    sbu_ids = fields.One2many('mngt.sbu', 'period_id', string='SBUs')

    total_net_revenue = fields.Float(compute='_compute_consolidated', store=True)
    total_contribution = fields.Float(compute='_compute_consolidated', store=True)
    total_profit_before_tax = fields.Float(compute='_compute_consolidated', store=True)
    total_profit_after_tax = fields.Float(compute='_compute_consolidated', store=True)

    @api.depends('sbu_ids.annual_net_revenue', 'sbu_ids.annual_contribution',
                 'sbu_ids.annual_profit_before_tax', 'sbu_ids.annual_profit_after_tax')
    def _compute_consolidated(self):
        for rec in self:
            rec.total_net_revenue = sum(rec.sbu_ids.mapped('annual_net_revenue'))
            rec.total_contribution = sum(rec.sbu_ids.mapped('annual_contribution'))
            rec.total_profit_before_tax = sum(rec.sbu_ids.mapped('annual_profit_before_tax'))
            rec.total_profit_after_tax = sum(rec.sbu_ids.mapped('annual_profit_after_tax'))


class MngtSbu(models.Model):
    _name = 'mngt.sbu'
    _description = 'Strategic Business Unit (DWBI)'
    _order = 'name'

    period_id = fields.Many2one('mngt.budget.period', string='Period', required=True,
                                default=lambda self: self.env['mngt.budget.period'].search(
                                    [('year', '=', str(datetime.now().year))], limit=1).id or
                                                     self.env['mngt.budget.period'].create({
                                                         'name': f"{datetime.now().year} Budget",
                                                         'year': str(datetime.now().year)
                                                     }).id)

    name = fields.Char(string='SBU Name', required=True, default='DWBI')

    soci_row_ids = fields.One2many('mngt.sbu.soci.row', 'sbu_id', string='SOCI Rows')

    expense_line_ids = fields.One2many('mngt.sbu.expense.line', 'sbu_id', string='SBU Expense Lines')

    onshore_impl_ids = fields.One2many('mngt.client.projection', 'sbu_id',
                                       domain=[('location_type', '=', 'onshore'),
                                               ('proj_category', '=', 'ongoing_impl')])
    onshore_existing_ids = fields.One2many('mngt.client.projection', 'sbu_id',
                                           domain=[('location_type', '=', 'onshore'),
                                                   ('proj_category', '=', 'existing_clients')])
    onshore_prospective_ids = fields.One2many('mngt.client.projection', 'sbu_id',
                                              domain=[('location_type', '=', 'onshore'),
                                                      ('proj_category', '=', 'prospective_clients')])
    offshore_impl_ids = fields.One2many('mngt.client.projection', 'sbu_id',
                                        domain=[('location_type', '=', 'offshore'),
                                                ('proj_category', '=', 'ongoing_impl')])
    offshore_existing_ids = fields.One2many('mngt.client.projection', 'sbu_id',
                                            domain=[('location_type', '=', 'offshore'),
                                                    ('proj_category', '=', 'existing_clients')])
    offshore_prospective_ids = fields.One2many('mngt.client.projection', 'sbu_id',
                                               domain=[('location_type', '=', 'offshore'),
                                                       ('proj_category', '=', 'prospective_clients')])

    mom_net_revenue = fields.Float(compute='_compute_annuals', store=True)
    mom_contribution = fields.Float(compute='_compute_annuals', store=True)
    mom_net_profit = fields.Float(compute='_compute_annuals', store=True)

    annual_net_revenue = fields.Float(compute='_compute_annuals', store=True)
    annual_contribution = fields.Float(compute='_compute_annuals', store=True)
    annual_profit_before_tax = fields.Float(compute='_compute_annuals', store=True)
    annual_profit_after_tax = fields.Float(compute='_compute_annuals', store=True)

    @api.depends('soci_row_ids')
    def _compute_annuals(self):
        for rec in self:
            rec.annual_net_revenue = sum(
                rec.soci_row_ids.filtered(lambda r: r.row_type == 'net_revenue').mapped('grand_total'))
            rec.annual_contribution = sum(
                rec.soci_row_ids.filtered(lambda r: r.row_type == 'contribution').mapped('grand_total'))
            rec.annual_profit_before_tax = sum(
                rec.soci_row_ids.filtered(lambda r: r.row_type == 'profit_before_tax').mapped('grand_total'))
            rec.annual_profit_after_tax = sum(
                rec.soci_row_ids.filtered(lambda r: r.row_type == 'profit_after_tax').mapped('grand_total'))

            rec.mom_net_revenue = rec.annual_net_revenue
            rec.mom_contribution = rec.annual_contribution
            rec.mom_net_profit = rec.annual_profit_after_tax

    @api.model
    def create(self, vals):
        if not vals.get('period_id'):
            vals['period_id'] = self.env['mngt.budget.period'].search(
                [('year', '=', str(datetime.now().year))], limit=1).id or self.env['mngt.budget.period'].create({
                'name': f"{datetime.now().year} Budget",
                'year': str(datetime.now().year)
            }).id

        record = super(MngtSbu, self).create(vals)

        # Removed (10, 'subtotal', 'SUBTOTAL', 'subtotal') line
        standard_rows = [
            (20, 'implementation', 'IMPLEMENTATION', 'input'),
            (30, 'amc', 'AMC', 'input'),
            (40, 'other_income', 'Other income(Fmbn training)', 'input'),
            (50, 'vat', 'VAT', 'input'),
            (60, 'business_cost', 'BUSINESS COST', 'input'),
            (70, 'net_revenue', 'NET REVENUE', 'net_revenue'),
            (80, 'direct_staff', 'DIRECT COST(SBU STAFF COST)', 'input'),
            (90, 'direct_exp', 'DIRECT COST(SBU EXPENSES)', 'input'),
            (100, 'direct_cost', 'DIRECT COST TOTAL', 'direct_cost'),
            (110, 'contribution', 'CONTRIBUTION', 'contribution'),
            (120, 'general_admin', 'GENERAL AND ADMINISTRATIVE EXPENSES', 'input'),
            (130, 'depreciation', 'DEPRECIATION AND AMORTISATION', 'input'),
            (140, 'personnel_shared', 'PERSONNEL COST - SHARED', 'input'),
            (150, 'profit_before_tax', 'PROFIT (LOSS) BEFORE TAXATION', 'profit_before_tax'),
            (160, 'tax_exp', 'INCOME TAX EXPENSES', 'input'),
            (170, 'profit_after_tax', 'NET PROFIT/LOSS', 'profit_after_tax'),
        ]

        for seq, label, name, row_type in standard_rows:
            self.env['mngt.sbu.soci.row'].create({
                'sbu_id': record.id,
                'sequence': seq,
                'row_label': label,
                'row_name': name,
                'row_type': row_type,
            })

        standard_expenses = [
            (10, 'Implementation Cost/Expenses'),
            (20, 'Local expenses'),
            (30, 'Hotel and accommodation'),
            (40, 'Foreign Travel expenses'),
            (50, 'Cost & Call to follow up on officer'),
            (60, 'Software'),
            (70, 'Training/License'),
            (80, 'Laptops and Computer items'),
            (90, 'Server'),
        ]

        for seq, name in standard_expenses:
            self.env['mngt.sbu.expense.line'].create({
                'sbu_id': record.id,
                'sequence': seq,
                'row_name': name,
            })

        return record

    # --- PARENT-LEVEL CALCULATION (INSTANT & DEDUCTIVE) ---
    @api.onchange('soci_row_ids')
    def _onchange_soci_row_ids(self):
        """Calculates row formulas live without subtotal. Expenses and taxes are strictly subtracted."""
        if not self.soci_row_ids:
            return

        months = [f'm{i}' for i in range(1, 13)]

        row_map = {row.row_label: row for row in self.soci_row_ids if row.row_label}

        def get_vals(row_key):
            row = row_map.get(row_key)
            if not row:
                return {m: 0.0 for m in months}
            return {m: getattr(row, m) or 0.0 for m in months}

        def set_vals(target_key, calculated_dict):
            target = row_map.get(target_key)
            if target:
                for m, val in calculated_dict.items():
                    setattr(target, m, val)

        # 1. NET REVENUE = (implementation + amc + other_income) - vat - business_cost
        imp = get_vals('implementation')
        amc = get_vals('amc')
        other = get_vals('other_income')
        vat = get_vals('vat')
        biz = get_vals('business_cost')

        net_revenue = {
            m: (imp[m] + amc[m] + other[m]) - vat[m] - biz[m] for m in months
        }
        set_vals('net_revenue', net_revenue)

        # 2. DIRECT COST TOTAL = direct_staff + direct_exp
        staff = get_vals('direct_staff')
        exp = get_vals('direct_exp')
        direct_cost = {m: staff[m] + exp[m] for m in months}
        set_vals('direct_cost', direct_cost)

        # 3. CONTRIBUTION = net_revenue - direct_cost
        contribution = {m: net_revenue[m] - direct_cost[m] for m in months}
        set_vals('contribution', contribution)

        # 4. PROFIT BEFORE TAX = contribution - admin - dep - personnel
        admin = get_vals('general_admin')
        dep = get_vals('depreciation')
        pers = get_vals('personnel_shared')
        pbt = {m: contribution[m] - admin[m] - dep[m] - pers[m] for m in months}
        set_vals('profit_before_tax', pbt)

        # 5. PROFIT AFTER TAX = profit_before_tax - tax_exp
        tax = get_vals('tax_exp')
        pat = {m: pbt[m] - tax[m] for m in months}
        set_vals('profit_after_tax', pat)

    @api.depends('onshore_impl_ids', 'onshore_existing_ids', 'onshore_prospective_ids',
                 'offshore_impl_ids', 'offshore_existing_ids', 'offshore_prospective_ids')
    def _auto_populate_implementation_from_clients(self):
        for sbu in self:
            # Find the Implementation row
            impl_row = sbu.soci_row_ids.filtered(lambda r: r.row_label == 'implementation')
            if not impl_row:
                continue

            # Collect all client records
            all_clients = sbu.onshore_impl_ids + sbu.onshore_existing_ids + sbu.onshore_prospective_ids + \
                          sbu.offshore_impl_ids + sbu.offshore_existing_ids + sbu.offshore_prospective_ids

            # Initialize monthly totals to 0
            monthly_totals = {f'm{i}': 0.0 for i in range(1, 13)}

            # Loop through clients and sum their monthly values
            for client in all_clients:
                # If Off-Shore, convert USD to NGN
                if client.location_type == 'offshore':
                    monthly_totals['m1'] += (client.m1 or 0.0) * (client.exchange_rate or 0.0)
                    monthly_totals['m2'] += (client.m2 or 0.0) * (client.exchange_rate or 0.0)
                    monthly_totals['m3'] += (client.m3 or 0.0) * (client.exchange_rate or 0.0)
                    monthly_totals['m4'] += (client.m4 or 0.0) * (client.exchange_rate or 0.0)
                    monthly_totals['m5'] += (client.m5 or 0.0) * (client.exchange_rate or 0.0)
                    monthly_totals['m6'] += (client.m6 or 0.0) * (client.exchange_rate or 0.0)
                    monthly_totals['m7'] += (client.m7 or 0.0) * (client.exchange_rate or 0.0)
                    monthly_totals['m8'] += (client.m8 or 0.0) * (client.exchange_rate or 0.0)
                    monthly_totals['m9'] += (client.m9 or 0.0) * (client.exchange_rate or 0.0)
                    monthly_totals['m10'] += (client.m10 or 0.0) * (client.exchange_rate or 0.0)
                    monthly_totals['m11'] += (client.m11 or 0.0) * (client.exchange_rate or 0.0)
                    monthly_totals['m12'] += (client.m12 or 0.0) * (client.exchange_rate or 0.0)
                else:
                    # On-Shore use amounts directly
                    monthly_totals['m1'] += (client.m1 or 0.0)
                    monthly_totals['m2'] += (client.m2 or 0.0)
                    monthly_totals['m3'] += (client.m3 or 0.0)
                    monthly_totals['m4'] += (client.m4 or 0.0)
                    monthly_totals['m5'] += (client.m5 or 0.0)
                    monthly_totals['m6'] += (client.m6 or 0.0)
                    monthly_totals['m7'] += (client.m7 or 0.0)
                    monthly_totals['m8'] += (client.m8 or 0.0)
                    monthly_totals['m9'] += (client.m9 or 0.0)
                    monthly_totals['m10'] += (client.m10 or 0.0)
                    monthly_totals['m11'] += (client.m11 or 0.0)
                    monthly_totals['m12'] += (client.m12 or 0.0)

            # Write to the Implementation row
            impl_row.write({
                'm1': monthly_totals['m1'],
                'm2': monthly_totals['m2'],
                'm3': monthly_totals['m3'],
                'm4': monthly_totals['m4'],
                'm5': monthly_totals['m5'],
                'm6': monthly_totals['m6'],
                'm7': monthly_totals['m7'],
                'm8': monthly_totals['m8'],
                'm9': monthly_totals['m9'],
                'm10': monthly_totals['m10'],
                'm11': monthly_totals['m11'],
                'm12': monthly_totals['m12'],
            })

    def action_bulk_input(self):
        """Opens the ONE wizard that handles bulk template download and import."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bulk Input Clients & Expenses (On-Shore & Off-Shore)',
            'res_model': 'mngt.bulk.input.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sbu_id': self.id,
            }
        }


class MngtSbuSociRow(models.Model):
    _name = 'mngt.sbu.soci.row'
    _description = 'Exact Rows in Image 8'
    _order = 'sequence'

    sbu_id = fields.Many2one('mngt.sbu', string='SBU', ondelete='restrict')
    sequence = fields.Integer(string='Seq', default=10)
    row_name = fields.Char(string='Row Name', readonly=True)

    # Removed ('subtotal', 'SUBTOTAL') from selection options
    row_label = fields.Selection([
        ('implementation', 'IMPLEMENTATION'),
        ('amc', 'AMC'),
        ('other_income', 'Other income(Fmbn training)'),
        ('vat', 'VAT'),
        ('business_cost', 'BUSINESS COST'),
        ('net_revenue', 'NET REVENUE'),
        ('direct_staff', 'DIRECT COST(SBU STAFF COST)'),
        ('direct_exp', 'DIRECT COST(SBU EXPENSES)'),
        ('direct_cost', 'DIRECT COST TOTAL'),
        ('contribution', 'CONTRIBUTION'),
        ('general_admin', 'GENERAL AND ADMINISTRATIVE EXPENSES'),
        ('depreciation', 'DEPRECIATION AND AMORTISATION'),
        ('personnel_shared', 'PERSONNEL COST - SHARED'),
        ('profit_before_tax', 'PROFIT (LOSS) BEFORE TAXATION'),
        ('tax_exp', 'INCOME TAX EXPENSES'),
        ('profit_after_tax', 'NET PROFIT/LOSS')
    ], string='SOCI Row', readonly=True)

    # Removed ('subtotal', 'Subtotal') from selection options
    row_type = fields.Selection([
        ('input', 'Input'),
        ('net_revenue', 'Net Revenue'),
        ('direct_cost', 'Direct Cost'),
        ('contribution', 'Contribution'),
        ('profit_before_tax', 'Profit Before Tax'),
        ('profit_after_tax', 'Profit After Tax')
    ], string='Row Type', readonly=True)

    # NEW FIELD: Used to lock fields in the XML
    is_readonly = fields.Boolean(string="Is Read Only", compute='_compute_is_readonly', store=True)

    m1 = fields.Float(string='Jan')
    m2 = fields.Float(string='Feb')
    m3 = fields.Float(string='Mar')
    m4 = fields.Float(string='Apr')
    m5 = fields.Float(string='May')
    m6 = fields.Float(string='Jun')
    m7 = fields.Float(string='Jul')
    m8 = fields.Float(string='Aug')
    m9 = fields.Float(string='Sep')
    m10 = fields.Float(string='Oct')
    m11 = fields.Float(string='Nov')
    m12 = fields.Float(string='Dec')

    q1 = fields.Float(compute='_compute_q', string='1st Q Total')
    q2 = fields.Float(compute='_compute_q', string='2nd Q Total')
    q3 = fields.Float(compute='_compute_q', string='3rd Q Total')
    q4 = fields.Float(compute='_compute_q', string='4th Q Total')
    grand_total = fields.Float(compute='_compute_q', string='Grand Total')

    @api.depends('row_type', 'row_label')
    def _compute_is_readonly(self):
        for rec in self:
            if rec.row_type != 'input' or rec.row_label == 'implementation':
                rec.is_readonly = True
            else:
                rec.is_readonly = False

    @api.depends('m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12')
    def _compute_q(self):
        for rec in self:
            months = [rec.m1, rec.m2, rec.m3, rec.m4, rec.m5, rec.m6, rec.m7, rec.m8, rec.m9, rec.m10, rec.m11, rec.m12]
            rec.q1 = sum(months[0:3])
            rec.q2 = sum(months[3:6])
            rec.q3 = sum(months[6:9])
            rec.q4 = sum(months[9:12])
            rec.grand_total = sum(months)


class MngtSbuExpenseLine(models.Model):
    _name = 'mngt.sbu.expense.line'
    _description = 'Exact Operating Expense Lines from Image 6'
    _order = 'sequence'

    sbu_id = fields.Many2one('mngt.sbu', string='SBU', ondelete='restrict')
    sequence = fields.Integer(string='Seq', default=10)
    row_name = fields.Char(string='Expense Item', readonly=True)
    justification = fields.Text(string='Justification', help='Explain why this expense is projected.')

    m1 = fields.Float(string='Jan')
    m2 = fields.Float(string='Feb')
    m3 = fields.Float(string='Mar')
    m4 = fields.Float(string='Apr')
    m5 = fields.Float(string='May')
    m6 = fields.Float(string='Jun')
    m7 = fields.Float(string='Jul')
    m8 = fields.Float(string='Aug')
    m9 = fields.Float(string='Sep')
    m10 = fields.Float(string='Oct')
    m11 = fields.Float(string='Nov')
    m12 = fields.Float(string='Dec')

    q1 = fields.Float(compute='_compute_q', string='1st Q Total')
    q2 = fields.Float(compute='_compute_q', string='2nd Q Total')
    q3 = fields.Float(compute='_compute_q', string='3rd Q Total')
    q4 = fields.Float(compute='_compute_q', string='4th Q Total')
    grand_total = fields.Float(compute='_compute_q', string='Grand Total')

    @api.depends('m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12')
    def _compute_q(self):
        for rec in self:
            months = [rec.m1, rec.m2, rec.m3, rec.m4, rec.m5, rec.m6, rec.m7, rec.m8, rec.m9, rec.m10, rec.m11, rec.m12]
            rec.q1 = sum(months[0:3])
            rec.q2 = sum(months[3:6])
            rec.q3 = sum(months[6:9])
            rec.q4 = sum(months[9:12])
            rec.grand_total = sum(months)


class MngtClientProjection(models.Model):
    _name = 'mngt.client.projection'
    _description = 'Images 2-5: Exact Client Projections'
    _order = 'client_name'

    sbu_id = fields.Many2one('mngt.sbu', string='SBU', ondelete='cascade')
    location_type = fields.Selection([
        ('onshore', 'On-Shore'),
        ('offshore', 'Off-Shore')
    ], string='Client Location', required=True)

    proj_category = fields.Selection([
        ('ongoing_impl', 'Ongoing Implementation'),
        ('existing_clients', 'Projects from Existing Fintrak Clients'),
        ('prospective_clients', 'Projects from Prospective Fintrak Clients')
    ], string='Client Category', required=True)

    client_name = fields.Char(string='Client')
    product = fields.Char(string='Product')

    amc = fields.Float(string='Annual Maintenance Charge')
    total_amount = fields.Float(string='Total Amount')

    usd = fields.Float(string='Other Currency(USD)')
    exchange_rate = fields.Float(string='Exchange rate')
    total_ngn = fields.Float(compute='_compute_ngn', string='Total in NGN')

    m1 = fields.Float(string='Jan')
    m2 = fields.Float(string='Feb')
    m3 = fields.Float(string='Mar')
    m4 = fields.Float(string='Apr')
    m5 = fields.Float(string='May')
    m6 = fields.Float(string='Jun')
    m7 = fields.Float(string='Jul')
    m8 = fields.Float(string='Aug')
    m9 = fields.Float(string='Sep')
    m10 = fields.Float(string='Oct')
    m11 = fields.Float(string='Nov')
    m12 = fields.Float(string='Dec')

    justification = fields.Text(string='Justification', help='Explain why this client amount is projected.')

    @api.depends('usd', 'exchange_rate', 'total_amount')
    def _compute_ngn(self):
        for rec in self:
            if rec.location_type == 'offshore':
                rec.total_ngn = rec.usd * rec.exchange_rate
            else:
                rec.total_ngn = rec.total_amount


class MngtBulkInputWizard(models.TransientModel):
    _name = 'mngt.bulk.input.wizard'
    _description = 'Bulk Input Wizard'

    sbu_id = fields.Many2one('mngt.sbu', string='SBU', required=True)
    file_to_import = fields.Binary(string='Upload Excel File')

    def action_download_template(self):
        """Downloads the human-friendly master template. GUIDE tab comes FIRST."""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError("Please install the 'xlsxwriter' library on your Odoo server.")

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # 1. SHEET #1: GUIDE - READ ME FIRST
        help_sheet = workbook.add_worksheet('GUIDE - READ ME FIRST')
        help_sheet.set_column('A:A', 100)
        help_sheet.write(0, 0, 'HOW TO FILL THIS TEMPLATE:')
        help_sheet.write(1, 0, 'STEP 1: Go to the "SBU Client Projection Inputs" sheet.')
        help_sheet.write(2, 0, 'STEP 2: In the "Client Location" column, use the dropdown to select:')
        help_sheet.write(3, 0, '    - On-Shore (for Nigerian clients)')
        help_sheet.write(4, 0, '    - Off-Shore (for foreign clients)')
        help_sheet.write(5, 0, '')
        help_sheet.write(6, 0, 'STEP 3: In the "Client Category" column, use the dropdown to select:')
        help_sheet.write(7, 0, '    - Ongoing (for current implementation projects)')
        help_sheet.write(8, 0, '    - Existing (for projects from existing Fintrak clients)')
        help_sheet.write(9, 0, '    - Prospective (for projects from prospective Fintrak clients)')
        help_sheet.write(10, 0, '')
        help_sheet.write(11, 0,
                         'STEP 4: Fill in the months (January to December) with the money you expect from the Client.')
        help_sheet.write(12, 0, 'STEP 5: For Off-Shore clients, fill in "Amount (USD)" and "Exchange Rate".')
        help_sheet.write(13, 0, '')
        help_sheet.write(14, 0, 'STEP 6: Save this Excel file. Upload it back in Odoo.')
        help_sheet.write(15, 0, 'QUESTIONS? Contact the Finance Team.')

        # 2. SHEET #2: SBU Client Projection Inputs (Only Client-level Revenue Info)
        sheet = workbook.add_worksheet('SBU Client Projection Inputs')

        headers = [
            'Client Location (On-Shore or Off-Shore)',
            'Client Category (Ongoing, Existing, or Prospective)',
            'Client Name',
            'Product',
            'Annual Maintenance Charge',
            'Total Amount',
            'Amount (USD)',
            'Exchange Rate',
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2'})
        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)

        # 3. DROPDOWNS
        # sheet.data_validation(1, 0, 1000, 0, {
        #     'validate': 'list', 'source': 'list', 'value': ['On-Shore', 'Off-Shore']
        # })
        # sheet.data_validation(1, 1, 1000, 1, {
        #     'validate': 'list', 'source': 'list', 'value': ['Ongoing', 'Existing', 'Prospective']
        # })

        # 3. DROPDOWN VALUES
        dropdown_sheet = workbook.add_worksheet('_DropdownLists')

        location_values = [
            'On-Shore',
            'Off-Shore',
        ]

        category_values = [
            'Ongoing',
            'Existing',
            'Prospective',
        ]

        # Write dropdown values
        for row_idx, value in enumerate(location_values):
            dropdown_sheet.write(row_idx, 0, value.strip())

        for row_idx, value in enumerate(category_values):
            dropdown_sheet.write(row_idx, 1, value.strip())

        # Hide the dropdown worksheet
        dropdown_sheet.hide()

        # 4. DATA VALIDATION DROPDOWNS

        # Client Location
        sheet.data_validation(1, 0, 1000, 0, {
            'validate': 'list',
            'source': "='_DropdownLists'!$A$1:$A$2",
            'dropdown': True,
            'ignore_blank': True,
        })

        # Client Category
        sheet.data_validation(1, 1, 1000, 1, {
            'validate': 'list',
            'source': "='_DropdownLists'!$B$1:$B$3",
            'dropdown': True,
            'ignore_blank': True,
        })

        # 4. MULTIPLE SAMPLE ROWS COVERING ALL CATEGORIES & LOCATIONS
        sample_rows = [
            # Row 1: On-Shore, Ongoing (April & August filled)
            ['On-Shore', 'Ongoing', 'Sample Bank', 'Monitoring', '', 500000, '', '', '', '', '', '', 100000, '', '', '',
             250000, '', '', '', '', ''],

            # Row 2: On-Shore, Existing (January & May filled)
            ['On-Shore', 'Existing', 'Existing Corp Ltd', 'Data Analytics', '', 300000, '', '', 50000, '', '', '', '',
             100000, '', '', '', '', '', '', '', ''],

            # Row 3: Off-Shore, Prospective (USD filled - October)
            ['Off-Shore', 'Prospective', 'Global Tech Inc', 'CREDIT MONITORING', '', '', 15000, 1600, '', '', '', '',
             '', '', '', '', '', '', 24000000, '', '', ''],

            # Row 4: Off-Shore, Ongoing (USD filled - July)
            ['Off-Shore', 'Ongoing', 'UK Finance Ltd', 'E-CHANNEL SOLUTION', '', '', 8000, 1600, '', '', '', '', '', '',
             '', 12800000, '', '', '', '', '', ''],
        ]

        # Write the rows with simple formatting
        simple_format = workbook.add_format({})
        for row_idx, row_data in enumerate(sample_rows):
            for col_idx, value in enumerate(row_data):
                # If it's a number, write as number; if it's a string, write as string
                if isinstance(value, (int, float)):
                    sheet.write_number(row_idx + 1, col_idx, value, simple_format)
                else:
                    sheet.write(row_idx + 1, col_idx, value, simple_format)

        workbook.close()
        output.seek(0)

        datas = base64.b64encode(output.read())
        attachment = self.env['ir.attachment'].create({
            'name': 'Master_SBU_Client_Projection_Template.xlsx',
            'datas': datas,
            'type': 'binary',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=1' % attachment.id,
            'target': 'new',
        }

    def action_import_file(self):
        """Imports the uploaded Excel file into the client projection tabs."""
        if not self.file_to_import:
            raise UserError("Please upload a file first.")

        try:
            import xlrd
        except ImportError:
            raise UserError("Please install the 'xlrd' library on your Odoo server.")

        try:
            workbook = xlrd.open_workbook(file_contents=base64.b64decode(self.file_to_import))
            sheet = workbook.sheet_by_name('SBU Client Projection Inputs')
        except Exception as e:
            raise UserError("Could not read the uploaded file. Please make sure you used the correct template.")

        # Start from row 1 (skip headers)
        for row_idx in range(1, sheet.nrows):
            row = sheet.row_values(row_idx)
            # Skip empty rows
            if not any(row):
                continue

            loc_text = str(row[0]).strip()
            cat_text = str(row[1]).strip()
            client_name = str(row[2]).strip()
            product = str(row[3]).strip()
            amc = row[4] if row[4] else 0.0
            total_amount = row[5] if row[5] else 0.0
            usd = row[6] if row[6] else 0.0
            exchange_rate = row[7] if row[7] else 0.0
            months = [row[8 + i] if row[8 + i] else 0.0 for i in range(12)]

            # Mapping texts to selections
            location_map = {'On-Shore': 'onshore', 'Off-Shore': 'offshore'}
            category_map = {'Ongoing': 'ongoing_impl', 'Existing': 'existing_clients',
                            'Prospective': 'prospective_clients'}

            location_type = location_map.get(loc_text)
            proj_category = category_map.get(cat_text)

            if not location_type or not proj_category:
                continue  # Skip invalid rows

            self.env['mngt.client.projection'].create({
                'sbu_id': self.sbu_id.id,
                'location_type': location_type,
                'proj_category': proj_category,
                'client_name': client_name,
                'product': product,
                'amc': amc,
                'total_amount': total_amount,
                'usd': usd,
                'exchange_rate': exchange_rate,
                'm1': months[0],
                'm2': months[1],
                'm3': months[2],
                'm4': months[3],
                'm5': months[4],
                'm6': months[5],
                'm7': months[6],
                'm8': months[7],
                'm9': months[8],
                'm10': months[9],
                'm11': months[10],
                'm12': months[11],
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }