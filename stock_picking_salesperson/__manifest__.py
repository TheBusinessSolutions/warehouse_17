{
    'name': 'Stock Picking Salesperson',
    'version': '17.0.1.0.0',
    'category': 'Warehouse',
    'summary': 'Add Salesperson name to Warehouse Delivery/Picking reports',
    'description': """
        This module adds the Salesperson's name to the stock picking report 
        (Delivery Orders, Receipts, etc.) beside the Source Document field.
    """,
    'author': 'Business Solutions',
    'website': 'https://www.thebusinesssolutions.net',
    'depends': ['stock', 'sale'], # Depends on sale to get the salesperson info
    'data': [
        'views/report_picking.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}