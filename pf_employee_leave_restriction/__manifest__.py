{
    'name': "HR Leave Restriction For Mandatory Days",
    'version': '16.0.1.0.0',
    'category': 'Human Resources',
    'sequence': -100,
    'summary': "Restrict employee leave on mandatory days with automatic validation and real-time warnings.",
    'license': 'OPL-1',
    'description': """
        Configure mandatory workdays and leave-restricted date ranges to automatically block non-compliant leave requests and ensure policy enforcement.
    """,
    'author': "Prefortune Technologies LLP",
    'website': "https://www.prefortune.com/",
    'maintainer': 'Prefortune Technologies LLP',
    "support": "odoo@prefortune.com",
    'currency': 'EUR',
	'price': '16.93',
    'depends': ['hr_holidays'],
    'data': [
        #'security/ir.model.access.csv',
        'views/mandatory_days_view.xml',
    ],

    "images": ["static/description/banner.png"],
    'installable' : True,
    'application': True,
    'auto_install' : False,

}
