# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime
import json
import werkzeug
import logging

_logger = logging.getLogger(__name__)


class QueuePickup(http.Controller):

    @http.route('/queue/pickup/listall', auth='public')
    def category_list(self, **kw):
        env_type = http.request.env['queue.pickup']
        args = [('state', '=', 'open')]
        type_ids = env_type.sudo().search_read(args)
        return json.dumps(type_ids)

    @http.route('/queue/pickupui/', auth='public')
    def pickupui(self, **kw):    
        env_pickup = http.request.env['queue.pickup']
        pickups = env_pickup.sudo().search([])
        return request.render('jakc_queue.pickupui', {'pickups': pickups})

    @http.route('/queue/pickup/screen/', type='http', auth='user')
    def queue_pickup_screen(self, **kwargs):
        # if user not logged in, log him in
        queue_trans_obj = http.request.env['queue.trans']
        pickup_log = http.request.env['queue.pickup.log'].search([
            ('state', '=', 'opened'),
            ('user_id', '=', http.request.session.uid), ], limit=1)
        if pickup_log:
            _logger.info(pickup_log)
            pickup_data = {}
            pickup_data.update({'pickup_id': pickup_log.pickup_id.id})
            return request.render('jakc_queue.pickupscreen', {'pickup': pickup_data})

    @http.route('/queue/pickup/current/<int:pickup_id>/', type='http', auth='user')
    def queue_pickup_current(self, pickup_id, **kwargs):
        queue_pickup_obj = http.request.env['queue.pickup']
        queue_pickup_log_obj = http.request.env['queue.pickup.log']
        queue_trans_obj = http.request.env['queue.trans']
        pickup = queue_pickup_obj.browse(pickup_id)
        if pickup:
            trans_args = [('state', '=', 'open'), ('type_id', '=', pickup.type_id.id)]
            trans_id = queue_trans_obj.search(trans_args, limit=1)
            if trans_id:
                trans_data = {}
                trans_data.update({'id': trans_id.id})
                trans_data.update({'counter_trans': trans_id.trans_id})
                trans_data.update({'counter_name': trans_id.type_id.name})
                trans_data.update({'counter_bg': trans_id.type_id.bg_color})
                return json.dumps(trans_data)
            else:
                return '{"success":false,"message":"No Queue"}'
        else:
            return '{"success":false,"message":"No Queue"}'

    @http.route('/queue/pickup/<int:id>/', auth='public')
    def pickup(self, id):
        queue_pickup_obj = http.request.env['queue.pickup']
        queue_pickup_log_obj = http.request.env['queue.pickup.log']
        queue_trans_obj = http.request.env['queue.trans']
        pickup = queue_pickup_obj.browse(id)
        if pickup:
            trans_args = [('state', '=', 'draft'), ('type_id', '=', pickup.type_id.id)]
            trans_id = queue_trans_obj.search(trans_args, order='create_date', limit=1)
            if trans_id:
                trans_id.write({'pickup_date_time': datetime.now(),
                                'state': 'open',
                                'type_id': pickup.type_id.id,
                                'iface_recall': True,
                                'recall_date_time': datetime.now(),
                                'pickup_id': pickup.id})
                trans_data = {}
                trans_data.update({'id': trans_id.id})
                trans_data.update({'counter_trans': trans_id.trans_id})
                trans_data.update({'counter_name': trans_id.type_id.name})
                trans_data.update({'counter_bg': trans_id.type_id.bg_color})
                return json.dumps(trans_data)
            else:
                return '{"success":false,"message":"No Queue"}'
        else:
            return '{"success":false,"message":"No Queue"}'

    @http.route('/queue/recall/<int:id>/', auth='public')
    def recall(self, id, **kwargs):
        queue_trans_obj = http.request.env['queue.trans']
        trans = queue_trans_obj.browse(id)
        trans.write({'recall_date_time': datetime.now(), 'iface_recall': True})
        return json.dumps({'status': True})

    @http.route('/queue/finish/<int:id>/', auth='public')
    def finish(self, id):
        queue_trans_obj = http.request.env['queue.trans']
        trans = queue_trans_obj.browse(id)
        trans.write({'end_date_time': datetime.now(), 'state': 'done'})
        return json.dumps({'status': True})

class Queue_display(http.Controller):
    
    @http.route('/queue/displayui/<display_code>/', auth='public')
    def displayui(self, display_code, **kw):
        return request.render('jakc_queue.index', {'displaycode': display_code})

    @http.route('/queue/routeui/<routing_code>', auth='public')
    def routeui(self, routing_code, **kw):
        return request.render('jakc_queue.routingscreen', {})
        
    @http.route('/queue/display/<display_code>/', auth='public')
    def display(self, display_code, **kw):
        env_display = http.request.env['queue.display']
        displays = env_display.sudo().search([('name','=',display_code)])
        display = displays[0]
        env_trans = request.env['queue.trans']
        transs = env_trans.sudo().search([('display_id','=',display.id),('state','=','open')])
        if transs:            
            trans = transs[0]       
            return '{"success":true,"message":"","trans_id": "' +  trans.trans_id + '"}'
        else:
            return '{"success":false,"message":""}'

    @http.route('/queue/routeui/listactive/<int:display_id>', auth='public')
    def display_list_active(self, display_id, **kw):
        queue_pickup_log_obj = http.request.env['queue.pickup.log']
        queue_pickup_obj = http.request.env['queue.pickup']
        queue_type_obj = http.request.env['queue.type']
        queue_trans_obj = http.request.env['queue.trans']
        pickup_log_args = [('state', '=', 'opened')]
        pickup_list = []
        pickup_log_ids = queue_pickup_log_obj.search(pickup_log_args)
        for pickup_log_id in pickup_log_ids:
            pickup_id = queue_pickup_obj.browse(pickup_log_id.pickup_id.id)
            if pickup_id.display_id.id == display_id:
                pickup_data = {}
                pickup_data.update({'pickup_name': pickup_id.name})
                pickup_data.update({'counter_name': pickup_id.type_id.name})
                queue_trans_args = [('pickup_id', '=', pickup_id.id), ('state', '=', 'open')]
                queue_trans = queue_trans_obj.search(queue_trans_args, limit=1)
                if queue_trans:
                    pickup_data.update({'current_trans': queue_trans.trans_id})
                else:
                    pickup_data.update({'current_trans': '---'})
                type_id = queue_type_obj.browse(pickup_id.type_id['id'])
                pickup_data.update({'counter_bg': type_id.bg_color})
                pickup_data.update({'counter_fa': 'fa-users'})
                pickup_data.update({'counter_code': '0001'})
                pickup_list.append(pickup_data)
        return json.dumps(pickup_list)

    @http.route('/queue/routeui/listnew/', auth='public')
    def display_list_new(self, **kw):
        queue_type_obj = http.request.env['queue.type']
        queue_trans_obj = http.request.env['queue.trans']
        trans_args = [('state', '=', 'draft')]
        trans_ids = queue_trans_obj.search(trans_args)
        trans_list = []
        for trans_id in trans_ids:
            trans_data = {}
            trans_data.update({'counter_name': trans_id.type_id.name})
            trans_data.update({'current_trans': trans_id.trans_id})
            trans_data.update({'counter_fa': 'fa-users'})
            trans_data.update({'counter_code': trans_id.type_id.name})
            trans_data.update({'counter_bg': trans_id.type_id.bg_color})
            trans_list.append(trans_data)
        return json.dumps(trans_list)

    @http.route('/queue/routeui/checksound/', auth='public')
    def checksound(self, **kw):
        queue_trans_obj = http.request.env['queue.trans']
        queue_trans_args = [('iface_recall', '=', True), ('state', '=', 'open')]
        queue_trans = queue_trans_obj.search(queue_trans_args, order='recall_date_time', limit=1)
        trans = {}
        if queue_trans:
            queue_trans.iface_recall = False
            trans.update({'status': True, 'counter_trans': queue_trans.trans_id, 'counter_number': queue_trans.pickup_id.name})
        else:
            trans.update({'status': False, 'counter_trans': {}})
        return json.dumps(trans)


class Queue_type(http.Controller):
    
    @http.route('/queue/type/listall', auth='public')
    def category_list(self, **kw):
        queue_type = http.request.env['queue.type']
        type_ids = queue_type.search([])
        types = []
        for type in type_ids:
            type_data = {}
            type_data.update({'counter_id': type.id})
            type_data.update({'counter_name': type.name})
            type_data.update({'counter_bg': type.bg_color})
            type_data.update({'counter_fa': 'fa-users'})
            types.append(type_data)
        return json.dumps(types)


class Queue_app(http.Controller):

    @http.route('/queue/kiosk/request/<int:type_id>/', auth='public', csrf=False)
    def app(self, type_id, **kw):
        try:
            queue_type_obj = http.request.env['queue.type']
            queue_trans_obj = http.request.env['queue.trans']
            trans_data = {}
            trans_data.update({'type_id': type_id})
            trans = queue_trans_obj.create(trans_data)
            trans_data = {}
            trans_data.update({'trans_id': trans.id})
            trans_data.update({'type_id': trans.type_id.id})
            trans_data.update({'counter_name': trans.type_id.name})
            trans_data.update({'counter_trans': trans.trans_id})
            trans_data.update({'counter_bg': trans.type_id.bg_color})
            return json.dumps(trans_data)
        except:
            return '{"success":false,"message":"Error"}'

    @http.route('/queue/receipt/<int:id>', auth='user')
    def queue_receipt(self, id, **kw):
        queue_trans_obj = http.request.env['queue.trans']
        queue_trans = queue_trans_obj.browse(id)
        if queue_trans:
            trans_data = {}
            trans_data.update({'counter_trans': queue_trans.trans_id})
            trans_data.update({'counter_type': queue_trans.type_id.name})
            return request.render('jakc_queue.receiptprint', {'data': trans_data})

    @http.route('/queue/kiosk', auth='public')
    def queue_kiosk(self, **kw):
        queue_type = http.request.env['queue.type']
        type_ids = queue_type.search([])
        for type in type_ids:
            type.mod_bg_color = 'btn3d btn btn-danger btn-lg btn-block'
        return request.render('jakc_queue.kioskscreen', {'types': type_ids})
