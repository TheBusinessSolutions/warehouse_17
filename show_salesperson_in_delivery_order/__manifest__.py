{
    'name': 'Show Salesperson in Delivery Order',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Displays the salesperson name on the delivery slip report.',
    'author': 'Coding Partner',
    'depends': ['stock', 'sale_stock'],
    'data': [
        'views/report_delivery_document_inherited.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}