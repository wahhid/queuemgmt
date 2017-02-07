from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_STATES = [
    ('draft','New'),
    ('open','Active'),    
    ('done','Closed'),
]

AVALABLE_DISPLAY_TYPE = [
    ('single','Single'),
    ('route','Route'),
]

AVAILABLE_PICKUP_TYPE = [
    ('desktop','Desktop'),
    ('device','Device'),
]

class queue_display(osv.osv):
    _name = "queue.display"
    _description = "Queue Display"
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'display_type': fields.selection(AVALABLE_DISPLAY_TYPE,'Display Type', size=16, required=True),
        'state': fields.selection(AVAILABLE_STATES, 'Status', size=16, required=True),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }
    
queue_display()

class queue_type(osv.osv):
    _name = "queue.type"
    _description = "Queue Type"
    
    def get_trans(self, cr, uid, ids, context=None):
        trans_id = ids[0]
        return self.browse(cr, uid, trans_id, context=context)
            
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'number': fields.integer('Number'),
        'is_active': fields.boolean('Is Active'),
        'state': fields.selection(AVAILABLE_STATES, 'Status', size=16, required=True),
    }
    _defaults = {
        'state': lambda *a: 'open',
    }

queue_type()

class queue_pickup(osv.osv):
    _name = "queue.pickup"
    _description = "Queue Pickup"
    
    def get_trans(self, cr, uid, ids, context=None):
        trans_id = ids[0]
        return self.browse(cr, uid, trans_id, context=context)
    
    def get_trans_by_name(self, cr, uid, name, context=None):
        args = [('name','=', name)]
        ids = self.search(cr, uid, args, context=context)
        if ids:
            return self.get_trans(cr, uid, ids, context=context)            
        else:
            return False
        
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'pickup_type': fields.selection(AVAILABLE_PICKUP_TYPE,'Pickup Type', size=16, required=True),
        'type_id' : fields.many2one('queue.type','Queue Type',required=True),
        'display_id' : fields.many2one('queue.display','Display', required=True),
        'is_active' : fields.boolean('Is Active'),
        'state' : fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True)
    }
    _defaults = {        
        'state': lambda *a: 'open',
    }

queue_pickup()
