from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [
    ('draft','New'),
    ('open','Active'),    
    ('done','Closed'),
]

AVAILABLE_PICKUP = [
    ('desktop','Desktop'),
    ('device','Device'),
]

AVAILABLE_PICKUP_LOG = [
    ('opened', 'In Progress'),
    ('closed', 'Closed & Posted'),
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

    @api.one
    def trans_close(self):
        self.state = 'done'

    @api.one
    def trans_reopen(self):
        self.state = 'open'


    name = fields.Char('Name', size=30, required=True)
    number = fields.Integer('Number', default=0)
    bg_color = fields.Selection(AVAILABLE_BG_COLOR, 'Bg Color', default='bg-red')
    mod_bg_color = fields.Char("Bg Color (String)", size=100, readonly=True)
    is_active = fields.Boolean('Active', default=False) 
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16 , readonly=True, default='open')


class QueuePickup(models.Model):
    _name = 'queue.pickup'

    @api.one
    def trans_open(self):
        self.state = 'open'

    @api.one
    def trans_close(self):
        self.state = 'done'

    @api.depends('pickup_log_ids')
    def _compute_current_pickup_log(self):
        for pickup in self:
            pickup_log = pickup.pickup_log_ids.filtered(lambda r: r.user_id.id == self.env.uid and \
                                                                  not r.state == 'closed')
            # sessions ordered by id desc
            pickup.current_pickup_log_id = pickup_log and pickup_log[0].id or False
            pickup.current_pickup_log_state = pickup_log and pickup_log[0].state or False

    @api.depends('pickup_log_ids')
    def _compute_current_pickup_user(self):
        for pickup in self:
            pickup_log = pickup.pickup_log_ids.filtered(lambda s: s.state == 'opened')
            pickup.pickup_log_username = pickup_log and pickup_log[0].user_id.name or False

    @api.multi
    def open_existing_pickup_log_cb_close(self):
        assert len(self.ids) == 1, "you can open only one session at a time"
        return self.open_pickup_log_cb()


    @api.multi
    def open_pickup_log_cb(self):
        assert len(self.ids) == 1, "you can open only one pickup log at a time"
        if not self.current_pickup_log_id:
            self.current_pickup_log_id = self.env['queue.pickup.log'].create({
                'user_id': self.env.uid,
                'pickup_id': self.id
            })
            if self.current_pickup_log_id.state == 'opened':
                return self.open_ui(self.current_pickup_log_id.id)
            return self._open_pickup_log(self.current_pickup_log_id.id)
        return self._open_pickup_log(self.current_pickup_log_id.id)

    @api.multi
    def open_existing_pickup_log_cb(self):
        assert len(self.ids) == 1, "you can open only one session at a time"
        return self._open_pickup_log(self.current_pickup_log_id.id)

    def _open_pickup_log(self, pickup_log_id):
        return {
            'name': _('Pickup Log'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'queue.pickup.log',
            'res_id': pickup_log_id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def open_ui(self, id):
        assert len(self.ids) == 1, "you can open only one session at a time"
        return {
            'type': 'ir.actions.act_url',
            'url': '/queue/pickup/screen/',
            'target': 'self',
        }

    name = fields.Char('Pickup Code', size=4, required=True)
    pickup_type = fields.Selection(AVAILABLE_PICKUP, 'Pickup Type', size=16, required=True)
    type_id = fields.Many2one('queue.type','Queue Type',index=True, required=True)
    display_id = fields.Many2one('queue.display','Display', index=True, required=True)
    pickup_log_ids = fields.One2many('queue.pickup.log', 'pickup_id', 'Logs', readonly=True)
    current_pickup_log_id = fields.Many2one('queue.pickup.log', compute='_compute_current_pickup_log',
                                            string='Current Pickup', store=False)
    current_pickup_log_state = fields.Selection(AVAILABLE_PICKUP_LOG, compute='_compute_current_pickup_log',
                                                string='Current State', store=False)
    pickup_log_username = fields.Char(compute='_compute_current_pickup_user', store=False)
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16, readonly=True, default='open')


class QueuePickupLog(models.Model):
    _name = 'queue.pickup.log'

    @api.one
    def trans_close(self):
        self.write({'log_out': datetime.now(), 'state': 'closed'})

    pickup_id = fields.Many2one('queue.pickup','Pickup',index=True)
    user_id = fields.Many2one('res.users', 'Operator', required=True, readonly=True)
    log_in = fields.Datetime('Log In', readonly=True, default=datetime.now())
    log_out = fields.Datetime('Log Out', readonly=True)
    state = fields.Selection(AVAILABLE_PICKUP_LOG, 'Status', size=16, readonly=True, default='opened')


class QueueTrans(models.Model):
    _name = 'queue.trans'

    trans_id = fields.Char('Transaction ID', size=4, required=False, readonly=True)
    trans_date = fields.Date('Date', required=True , default=fields.Date.today)
    type_id = fields.Many2one('queue.type', 'Type', required=True, index=True)
    display_id = fields.Many2one('queue.display','Display',index=True)
    pickup_id = fields.Many2one('queue.pickup', 'Pickup', index=True)
    start_date_time = fields.Datetime('Start Time', default=fields.Datetime.now)
    is_pickup = fields.Boolean('Is Pickup', default=False)    
    pickup_date_time = fields.Datetime('Pickup Time')    
    end_date_time = fields.Datetime('End Time')
    iface_recall = fields.Boolean('Re-call', default=False)
    recall_date_time = fields.Boolean('Re-call Time')
    printed = fields.Boolean('Printed',default=False)    
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16, readonly=True , default='draft')

    @api.model
    def create(self,values):
        queue_type_obj = self.env['queue.type']
        queue_trans_obj = self.env['queue.trans']
        trans_id = '000'
        if 'type_id' in values.keys():
            trans_args = [
                ('type_id', '=', values.get('type_id')), ('trans_date', '=', datetime.now().strftime('%Y-%m-%d'))]
            queue_trans_ids = queue_trans_obj.search(trans_args)
            if len(queue_trans_ids) > 0:
                trans_id = str(len(queue_trans_ids) + 1).zfill(3)
            else:
                trans_id = str(1).zfill(3)
        values.update({'trans_id': trans_id})
        result = super(QueueTrans,self).create(values)
        # trans_data = {}
        # trans_data.update({'trans_id': result.id})
        # self.env['queue.trans.print'].create(trans_data)
        # self.env['queue.trans.sound'].create(trans_data)
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