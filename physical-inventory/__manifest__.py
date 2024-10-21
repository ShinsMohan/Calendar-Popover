{
    'name': 'Warehouse Adjustment Reason',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Collect reason for inventory adjustments and store in stock move lines',
    'author': 'Your Name',
    'depends': ['stock'],
    'data': [
        'wizard/adjustment_reason_wizard_view.xml',
        'views/stock_move_line_view.xml',
    ],
    'installable': True,
    'application': False,
}
