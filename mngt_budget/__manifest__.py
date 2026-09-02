{
    'name': 'Management Accounting Full Replica',
    'version': '16.0.1.0.0',
    'category': 'Management',
    'summary': 'Fintrak Budget Management',
    'depends': ['base', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/mngt_budget_menus.xml',
        'views/mngt_budget_views.xml',
    ],
    'installable': True,
    'application': False,
}