from collections import defaultdict
from odoo import models, fields
from datetime import datetime, timedelta

def is_weekend(date):
    """Check if the given date is a weekend (Saturday/Sunday)."""
    return date.weekday() in (5, 6)  # 5 is Saturday, 6 is Sunday

def get_public_holidays(public_holidays):
    """Retrieve public holidays from Odoo's resource.calendar.leaves (or a custom model)."""
    holidays = public_holidays.search([
        ('resource_id', '=', False)  # Public holidays that are not resource-specific
    ])
    holiday_dates = []
    for holiday in holidays:
        date_from = holiday.date_from
        date_to = holiday.date_to
        
        # Generate the date range from date_from to date_to (inclusive)
        current_date = date_from
        while current_date <= date_to:
            if current_date.weekday() not in (5, 6):
                holiday_dates.append(current_date)
            current_date += timedelta(days=1)
    
    return holiday_dates

def calculate_working_hours(start_datetime: datetime, end_datetime: datetime, public_holidays: list):
    """Calculate the number of working hours between two datetimes, excluding weekends and public holidays."""
    total_working_hours = 0.0
    current_datetime = start_datetime
    
    # Iterate through each day from start to end
    while current_datetime.date() <= end_datetime.date():
        if not is_weekend(current_datetime.date()) and current_datetime.date() not in public_holidays:
            # On the first day, we may not count the full day
            if current_datetime.date() == start_datetime.date():
                if current_datetime.date() == end_datetime.date():
                    # Both start and end are on the same day
                    total_working_hours += (end_datetime - start_datetime).total_seconds() / 3600
                else:
                    # Count from start_datetime to end of that day
                    day_end = current_datetime.replace(hour=23, minute=59, second=59)
                    total_working_hours += (day_end - start_datetime).total_seconds() / 3600
            # On the last day, count from the beginning of the day to end_datetime
            elif current_datetime.date() == end_datetime.date():
                day_start = end_datetime.replace(hour=0, minute=0, second=0)
                total_working_hours += (end_datetime - day_start).total_seconds() / 3600
            else:
                # Full day working hours (24 hours)
                total_working_hours += 24  # 24 hours for full days
        
        # Move to the next day
        current_datetime += timedelta(days=1)
    
    return total_working_hours



class DeliveryAnalysisReport(models.AbstractModel):
    _name = 'report.delivery_analysis_report.delivery_analysis_excel'
    _description = 'Delivery Analysis Report'
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        state = data.get('state')

        domain = [('partner_id', '!=', False), ('picking_type_id.code', '=', 'outgoing')]

        if start_date:
            domain.append(('date_done', '>=', start_date))

        if end_date:
            domain.append(('date_done', '<=', end_date))
        
        if state:
            domain.append(('state', '=', state))    

        stock_pickings = self.env['stock.picking'].search(domain)

        public_holidays = get_public_holidays(self.env['resource.calendar.leaves'])

        company_data = {}

        for picking in stock_pickings.sorted(key=lambda x: x.partner_id.parent_id.name if x.partner_id.parent_id else x.partner_id.name):
            partner = picking.partner_id
            company_id = partner.parent_id.id if partner.parent_id else partner.id
            company_name = partner.parent_id.name if partner.parent_id else partner.name

            # Calculate delay (exclude weekends and public holidays, using datetime)
            if picking.date_done and picking.scheduled_date:
                delay_hours = calculate_working_hours(picking.scheduled_date, picking.date_done, public_holidays)
                delay = delay_hours / 24  # Convert to days
            else:
                delay = 0

            # Calculate cycle time (exclude weekends and public holidays, using datetime)
            if picking.date_done and picking.date:
                cycle_hours = calculate_working_hours(picking.date, picking.date_done, public_holidays)
                cycle_time = cycle_hours / 24  # Convert to days
            else:
                cycle_time = 0

            # Initialize company data if not already there
            if company_id not in company_data:
                company_data[company_id] = {
                    'company_name': company_name,
                    'total_pickings': 0,
                    'on_time_pickings': 0,
                    'delayed_pickings': 0,
                    'total_delay': 0,
                    'total_cycle_time': 0
                }

            # Update counts and times
            company_data[company_id]['total_pickings'] += 1
            company_data[company_id]['total_delay'] += delay
            company_data[company_id]['total_cycle_time'] += cycle_time
            if picking.scheduled_date >= picking.date_done:
                company_data[company_id]['on_time_pickings'] += 1
            else:
                company_data[company_id]['delayed_pickings'] += 1

        # Process the aggregated data
        result = []
        for company_id, data in company_data.items():
            total_pickings = data['total_pickings']
            on_time_percentage = (data['on_time_pickings'] / total_pickings * 100) if total_pickings else 0
            result.append({
                'company_id': company_id,
                'company_name': data['company_name'],
                'delay': round(data['total_delay'] / total_pickings, 2),
                'cycle_time': round(data['total_cycle_time'] / total_pickings, 2),
                'total_pickings': total_pickings,
                'on_time_pickings': data['on_time_pickings'],
                'delayed_pickings': data['delayed_pickings'],
                'on_time_percentage': round(on_time_percentage, 2)
            })

        
        # Creating Excel
        worksheet = workbook.add_worksheet('Delivery Analysis')

        main_heading_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4F81BD',
            'font_color': 'white',
            'border': 1
        })

        sub_heading_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#9BC2E6',
            'font_color': 'black',
            'border': 1 
        })

        left = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1  # Add border
        })

        right = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'border': 1  # Add border
        })

        # Write main heading and subheading
        headers = ["Main Customer", "Average Cycle Time (Days)", "Average Delays (Days)", "No. of Deliveries", "On-Time Deliveries", "Delayed Deliveries", "On-Time Deliveries (%)"]
        worksheet.merge_range(0, 0, 0, len(headers)-1, self.env.company.name, main_heading_format)
        worksheet.merge_range(1, 0, 1, len(headers)-1, 'Delivery Analysis', main_heading_format)
        worksheet.write_row(2, 0, headers, sub_heading_format)

        # Dynamically calculate column widths based on header lengths
        padding = 1
        column_widths = [len(header) + padding for header in headers]

        # Apply column widths
        for i, width in enumerate(column_widths):
            worksheet.set_column(i, i, width)

        # Write data rows
        for row_index, row in enumerate(result, start=3):
            worksheet.write(row_index, 0, row['company_name'], left)
            worksheet.write(row_index, 1, row['cycle_time'], right)
            worksheet.write(row_index, 2, row['delay'], right)
            worksheet.write(row_index, 3, row['total_pickings'], right)
            worksheet.write(row_index, 4, row['on_time_pickings'], right)
            worksheet.write(row_index, 5, row['delayed_pickings'], right)
            worksheet.write(row_index, 6, row['on_time_percentage'], right)


class detailedDeliveryAnalysisReport(models.AbstractModel):
    _name = 'report.delivery_analysis_report.det_delivery_analysis_excel'
    _description = 'Detailed Delivery Analysis Report'
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        state = data.get('state')

        domain = [('partner_id', '!=', False), ('picking_type_id.code', '=', 'outgoing')]

        if start_date:
            domain.append(('date_done', '>=', start_date))

        if end_date:
            domain.append(('date_done', '<=', end_date))
        
        if state:
            domain.append(('state', '=', state))    

        stock_pickings = self.env['stock.picking'].search(domain)

        public_holidays = get_public_holidays(self.env['resource.calendar.leaves'])

        # Group results using res_partner for child and main companies
        grouped_results = defaultdict(list)

        for picking in stock_pickings.sorted(key=lambda x: x.partner_id.parent_id.name if x.partner_id.parent_id else x.partner_id.name):
            partner = picking.partner_id
            main_company = partner.parent_id if partner.parent_id else partner

            # Calculate delay (exclude weekends and public holidays, using datetime)
            if picking.date_done and picking.scheduled_date:
                delay_hours = calculate_working_hours(picking.scheduled_date, picking.date_done, public_holidays)
                delay = delay_hours / 24  # Convert to days
            else:
                delay = 0

            # Calculate cycle time (exclude weekends and public holidays, using datetime)
            if picking.date_done and picking.date:
                cycle_hours = calculate_working_hours(picking.date, picking.date_done, public_holidays)
                cycle_time = cycle_hours / 24  # Convert to days
            else:
                cycle_time = 0

            grouped_results[main_company.id].append({
                'main_company_name': main_company.name,
                'child_company_name': partner.name,
                'picking_name': picking.name,
                'delay': round(delay, 2),
                'cycle_time': round(cycle_time, 2),
                'total_pickings': 1,
                'on_time_pickings': 1 if picking.scheduled_date >= picking.date_done else 0,
                'delayed_pickings': 1 if picking.scheduled_date < picking.date_done else 0,
            })
        
        # Creating Excel
        worksheet = workbook.add_worksheet('Delivery Analysis')

        main_heading_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4F81BD',
            'font_color': 'white',
            'border': 1
        })

        sub_heading_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#9BC2E6',
            'font_color': 'black',
            'border': 1 
        })

        left = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1  # Add border
        })

        right = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'border': 1  # Add border
        })

        boldc = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bold': True
        })

        boldl = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
            'bold': True
        })

        boldr = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'bold': True
        })

        # Write main heading and subheading
        headers = ["Main Customer", "delivery Contact", "Deliver Order Number", "Average Cycle Time (Days)", "Average Delays (Days)", "No. of Deliveries", "On-Time Deliveries", "Delayed Deliveries", "On-Time Deliveries (%)"]
        worksheet.merge_range(0, 0, 0, len(headers)-1, self.env.company.name, main_heading_format)
        worksheet.merge_range(1, 0, 1, len(headers)-1, 'Delivery Analysis', main_heading_format)
        worksheet.write_row(2, 0, headers, sub_heading_format)

        # Dynamically calculate column widths based on header lengths
        padding = 1
        column_widths = [len(header) + padding for header in headers]

        # Apply column widths
        for i, width in enumerate(column_widths):
            worksheet.set_column(i, i, width)

        # Initialize the row index
        row_index = 3  # Start after headers

        for main_company_id, records in grouped_results.items():
            # Aggregate totals for each main company
            total_cycle_time = round(sum(record['cycle_time'] for record in records) / len(records), 2)
            total_delay = round(sum(record['delay'] for record in records) / len(records), 2)
            total_pickings = sum(record['total_pickings'] for record in records)
            on_time_pickings = sum(record['on_time_pickings'] for record in records)
            delayed_pickings = sum(record['delayed_pickings'] for record in records)
            on_time_percentage = (on_time_pickings / total_pickings * 100) if total_pickings else 0

            # Write main company totals
            worksheet.write(row_index, 0, records[0]['main_company_name'], boldl)
            worksheet.write(row_index, 1, '', boldl)
            worksheet.write(row_index, 2, '', boldl)
            worksheet.write(row_index, 3, total_cycle_time, boldr)
            worksheet.write(row_index, 4, total_delay, boldr)
            worksheet.write(row_index, 5, total_pickings, boldr)
            worksheet.write(row_index, 6, on_time_pickings, boldr)
            worksheet.write(row_index, 7, delayed_pickings, boldr)
            worksheet.write(row_index, 8, round(on_time_percentage, 2), boldr)

            row_index += 1

            # Write detailed records for each picking
            for record in records:
                worksheet.write(row_index, 0, '', left)
                worksheet.write(row_index, 1, record['child_company_name'], left)
                worksheet.write(row_index, 2, record['picking_name'], left)
                worksheet.write(row_index, 3, record['cycle_time'], right)
                worksheet.write(row_index, 4, record['delay'], right)
                worksheet.write(row_index, 5, record['total_pickings'], right)
                worksheet.write(row_index, 6, record['on_time_pickings'], right)
                worksheet.write(row_index, 7, record['delayed_pickings'], right)
                worksheet.write(row_index, 8, '', right)

                row_index += 1

