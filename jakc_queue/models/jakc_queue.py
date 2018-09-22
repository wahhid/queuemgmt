from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning
from datetime import datetime

AVAILABLE_STATES = [
    ('draft','New'),
    ('open','Active'),    
    ('done','Closed'),
]

AVAILABLE_PICKUP = [
    ('desktop','Desktop'),
    ('device','Device'),
]

AVAILABLE_DISPLAY = [
    ('single','Single'),
    ('route','Route'),
]

AVAILABLE_BG_COLOR = [
    ('bg-red', 'bg-red'),
    ('bg-yellow', 'bg-yellow'),
    ('bg-aqua', 'bg-aqua'),
    ('bg-blue', 'bg-blue'),
    ('bg-light-blue', 'bg-light-blue'),
    ('bg-green', 'bg-green'),
    ('bg-navy', 'bg-navy'),
    ('bg-teal', 'bg-teal'),
    ('bg-olive', 'bg-olive'),
    ('bg-lime', 'bg-lime'),
    ('bg-orange', 'bg-orange'),
    ('bg-fuchsia', 'bg-fuchsia'),
    ('bg-purple', 'bg-purple'),
    ('bg-maroon', 'bg-maroon'),
    ('bg-black', 'bg-black'),
]


class QueueDisplay(models.Model):
    _name = 'queue.display'

    name = fields.Char('Display Code', size=4, required=True)
    display_type = fields.Selection(AVAILABLE_DISPLAY,'Display Type', size=16, required=True)
    font_size = fields.Integer('Font Size',default=10)
    state = fields.Selection(AVAILABLE_STATES,'Status',size=16,readonly=True, default='open')
      

class QueueType(models.Model):
    _name = 'queue.type'

    name = fields.Char('Name', size=30, required=True)
    number = fields.Integer('Number', default=0)
    bg_color = fields.Selection(AVAILABLE_BG_COLOR, 'Bg Color', default='bg_black')
    is_active = fields.Boolean('Active', default=False) 
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16 , readonly=True, default='open')


class QueuePickup(models.Model):
    _name = 'queue.pickup'

    name = fields.Char('Pickup Code', size=4, required=True)
    pickup_type = fields.Selection(AVAILABLE_PICKUP, 'Pickup Type', size=16, required=True)
    type_id = fields.Many2one('queue.type','Queue Type',index=True, required=True)
    display_id = fields.Many2one('queue.display','Display', index=True, required=True)
    is_active = fields.Boolean('Is Active',default=False)
    session_ids = fields.One2many('queue.pickup.session')
    current_session_id = fields.Many2one('queue.pikcup.session')
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16, readonly=True, default='open')


class QueuePickupSession(models.Model):
    _name = 'queue.pickup.session'

    name = fields.Char('Pickup Code', size=4, required=True)
    date = fields.Date('Date', default=datetime.today())
    user_id = fields.Many2one('res.users', 'Operator', required=True)
    state = fields.Selection()


class QueuePickupLog(models.Model):
    _name = 'queue.pickup.log'

    pickup_id = fields.Many2one('queue.pickup','Pickup',index=True)
    queue_type_id = fields.Many2one('queue.type','Queue Type',index=True)
    log_in = fields.Datetime('Log In')
    log_out = fields.Datetime('Log Out')
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16, readonly=True , default='open')


class QueueTrans(models.Model):
    _name = 'queue.trans'

    trans_id = fields.Char('Transaction ID', size=4, required=True)
    trans_date = fields.Date('Date', required=True , default=fields.Date.today)
    type_id = fields.Many2one('queue.type', 'Type', index=True)
    display_id = fields.Many2one('queue.display','Display',index=True)
    start_date_time = fields.Datetime('Start Time', default=fields.Datetime.now)
    is_pickup = fields.Boolean('Is Pickup', default=False)    
    pickup_date_time = fields.Datetime('Pickup Time')    
    end_date_time = fields.Datetime('End Time')
    printed = fields.Boolean('Printed',default=False)    
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16, readonly=True , default='draft')

    @api.model
    def create(self,values):
        result = super(QueueTrans,self).create(values)
        trans_data = {}
        trans_data.update({'trans_id': result.id})
        self.env['queue.trans.print'].create(trans_data)
        self.env['queue.trans.sound'].create(trans_data)
        return result
        
        
class QueueTransPrint(models.Model):
    _name = 'queue.trans.print'
    trans_id = fields.Many2one('queue.trans', 'Transaction ID', index=True)
    trans_date_time = fields.Datetime('Date and Time', default=fields.Datetime.now)
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16, readonly=True, default='open')
    

class QueueTransSound(models.Model):
    _name = 'queue.trans.sound'
    trans_id = fields.Many2one('queue.trans', 'Transaction ID', index=True)
    trans_date_time = fields.Datetime('Date and Time', default=fields.Datetime.now)
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16, readonly=True, default='open')