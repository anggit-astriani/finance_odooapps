{
    'name': 'Module Custom Purchase',
    'version': '17.0.1.0',
    'category': 'Purchase',
    'summary': 'Module Custom Purchase',
    'description': """
        Purchase Custome Module by Anggit
    """,
    'website': '',
    'author': 'Anggit',
    'depends': ['web','base', 'product', 'account', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/anggit_purchase_view.xml',
        'views/anggit_purchase_action.xml',
        'views/anggit_purchase_menuitem.xml',
        'views/anggit_purchase_inv_sequence.xml',
        'views/res_config_settings_view.xml'
    ],
    'installable': True,
    'license': 'OEEL-1'
}