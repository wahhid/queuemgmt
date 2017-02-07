from openerp.osv import fields, osv
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_STATES = [
    ('draft','New'),
    ('request_pickup','Request Pickup'),
    ('pickup','Pickup'),
    ('open','Active'),    
    ('done','Closed'),
]

class queue_trans(osv.osv):
    _name = "queue.trans"
    _description = "Queue Transaction"
    
    def get_trans(self, cr, uid, ids, context=None):
        trans_id = ids[0]
        return self.browse(cr, uid, trans_id, context=context)
    
    def get_trans_by_type(self, cr, uid, type_id, context=None):
        args = [('type_id','=', type_id),('state','=','new')]
        ids = self.browse(cr, uid, args, context=context)
        if ids:
            return self.get_trans(cr, uid, ids, context=context)
        else:
            raise osv.except_osv(('Warning'), ('Transaction not Found'))    
        
    def trans_request_pickup(self, cr, uid, ids, context=None):
        values = {}
        values.update({'state':'request_pickup'})
        return self.write(cr, uid, ids, values, context=context)
    
    def request_pickup(self, cr, uid, ids, values, context=None):
        trans = self.get_trans(cr, uid, ids, context=context)        
        type_id = trans.type_id                
        if type_id:            
            trans = self.get_trans_by_type(cr, uid, type_id.id, context=context)
            if trans:                
                display_id = type_id.display_id
                values.update({'display_id': display_id.id})
                values.update({'pickup_date_time': datetime.now()})
                values.update({'state': 'pickup'})
                return super(queue_trans, self).write(cr, uid, ids, values, context=context)
                        
    _columns = {
        'trans_id' : fields.char('Transaction ID', size=4, required=True),
        'trans_date' : fields.date('Date', required=True),
        'type_id' : fields.many2one('queue.type', 'Type'),
        'display_id' : fields.many2one('queue.display','Display'),
        'start_date_time' : fields.datetime('Start Time'),
        'is_pickup' : fields.boolean('Is Pickup'),    
        'pickup_date_time' : fields.datetime('Pickup Time'),    
        'end_date_time' : fields.datetime('End Time'),
        'printed' : fields.boolean('Printed'),    
        'state' : fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True)        
    }
    _defaults = {
        'trans_date': fields.date.context_today,
        'start_date_time': fields.datetime.now,
        'printed': lambda *a: False,
        'state': lambda *a: 'draft',
    }
    
    def create(self, cr, uid, values, context=None):
        type_id = values.get('type_id')        
        type = self.pool.get('queue.type').browse(cr, uid, type_id, context=context)
        if type:                              
            number =  type.number + 1
            type_data = {}
            type_data.update({'number': number})
            result = self.pool.get('queue.type').write(cr, uid, [type_id], type_data, context=context)
            if result:
                str_number = str(number)
                if len(str_number) == 1:
                    str_number = '00' + str_number
                elif len(str_number) == 2 :
                    str_number = '0' + str_number                                                   
                values.update({'trans_id': str_number})                            
                result_id = super(queue_trans, self).create(cr, uid, values, context=context)
                return result_id                
            else:
                raise osv.except_osv(('Warning'), ('Type not Found'))
        else:
            raise osv.except_osv(('Warning'), ('Type not Found'))    
        
    def write(self, cr, uid, ids, values, context=None):
        trans = self.get_trans(cr, uid, ids, context=context)
        if trans.state == 'done':
            raise osv.except_osv(('Warning'), ('Transaction Already Closed'))
        
        if 'state' in values.keys():
            if values.get('state') == 'request_pickup':
                return self.request_pickup(cr, uid, ids, values, context=context)
        
        
                                            
queue_trans()                            