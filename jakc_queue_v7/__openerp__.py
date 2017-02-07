{
    'name' : 'Queue Management System',
    'version' : '1.0',
    'author' : 'Jakc Labs',
    'category' : 'Generic Modules/Queue Management System',
    'depends' : ['base_setup','base'],
    'init_xml' : [],
    'data' : [             
        'jakc_queue_view.xml',
        'jakc_queue_trans_view.xml',                
        'jakc_queue_menu.xml',         
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}