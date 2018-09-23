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

    def _trans_close(self, trans):
        trans_data = {}
        trans_data.update({'end_time': datetime.now().strftime('%Y-%m-%d')})
        trans_data.update({'state': 'done'})
        trans.sudo().write(trans_data)            
    
    @http.route('/queue/pickupsound/', auth='public')
    def appprint(self, **kw):
        env_trans_print = http.request.env['queue.trans.sound']
        transs = env_trans_print.sudo().search([('state','=','open')])
        if transs:
            trans = transs[0]
            trans_data = {}
            trans_data.update({'state': 'done'})
            trans.sudo().write(trans_data)            
            return '{"success":true,"message":"","trans_id":"' + trans.trans_id.trans_id + '"}'
        else:
            return '{"success":false,"message":"No Sound Data"}'

    @http.route('/queue/pickupui/', auth='public')
    def pickupui(self, **kw):    
        env_pickup = http.request.env['queue.pickup']
        pickups = env_pickup.sudo().search([])
        return request.render('jakc_queue.pickupui', {'pickups': pickups})

    @http.route('/queue/pickup/screen/<int:id>', type='http', auth='user')
    def queue_pickup_screen(self, id):
        # if user not logged in, log him in
        pickup_logs = http.request.env['queue.pickup.log'].search_read([
            ('state', '=', 'opened'),
            ('user_id', '=', http.request.session.uid), ], limit=1)
        if len(pickup_logs) == 1:
            pickup_log = pickup_logs[0]
            _logger.info(pickup_log)
            pickup_data = {}
            pickup_data.update({'pickup_id': pickup_log['pickup_id'][0]})
            return request.render('jakc_queue.pickupscreen', {'pickup': pickup_data})

    @http.route('/queue/pickup/<int:id>/', auth='public')
    def pickup(self, id):
        env_pickup = http.request.env['queue.pickup']
        pickup = env_pickup.sudo().browse(id)
        type_id = pickup.type_id
        display_id = pickup.display_id
        env_trans = http.request.env['queue.trans']
        trans_ids = env_trans.sudo().search([('type_id', '=', type_id.id), ('state', '=', 'draft')],
                                            order='create_date', limit=1)
        if len(trans_ids) == 1:
            trans_id = env_trans.sudo().browse(trans_ids[0])
            trans_data = {}
            trans_data.update({'display_id': display_id.id})
            trans_data.update({'pickup_date_time': datetime.now()})
            trans_data.update({'state': 'open'})
            trans_id.sudo().write(trans_data)
            return '{"success":true,"message":"Pickup Successfully","trans_id":"' + trans_id.trans_id + '"}'
        else:
            return '{"success":false,"message":"No Queue"}'


class Queue_display(http.Controller):
    
    @http.route('/queue/displayui/<display_code>/', auth='public')        
    def displayui(self, display_code):
        return request.render('jakc_queue.index', {'displaycode': display_code})

    @http.route('/queue/routeui/', auth='public')        
    def routeui(self, **kw):
        return request.render('jakc_queue.routingscreen', {})
        
    @http.route('/queue/display/<display_code>/', auth='public')
    def display(self, display_code):
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
            

class Queue(http.Controller):
    @http.route('/queue/queue/<int:id>', auth='public')
    def index(self, id):
        Types = http.request.env['queue.type']
        return http.request.render('jakc_queue.index', {
            'types': Types.search([('id','=', id)])
        })


class Queue_type(http.Controller):
    
    @http.route('/queue/type/listall', auth='public')
    def category_list(self, **kw):
        env_type =  http.request.env['queue.type']
        type_ids = env_type.sudo().search_read([])
        types = []
        for type in type_ids:
            type_data = {}
            type_data.update({'counter_id': type.id})
            type_data.update({'counter_name': type.name})
            type_data.update({'counter_bg': type.bg_color})
            type_data.update({'counter_fa': 'fa-users'})
            type_data.update({'counter_trans': '000'})
            types.append(type_data)
        return json.dumps(types)


class Queue_app(http.Controller):
    
    def trans_close(self):
        trans_data = {}
        trans_data.update({'end_time': datetime.now().strftime('%Y-%m-%d')})
        trans_data.update({'state':'done'})
        return True
        
    @http.route('/queue/appui/', auth='public')
    def appui(self, **kw):
        env_type = http.request.env['queue.type']
        types = env_type.sudo().search([])                 
        return http.request.render('jakc_queue.appui', {'types':types})

    @http.route('/queue/app/<int:type_id>/', auth='public')
    def app(self, type_id):
        try:
            env_type = http.request.env['queue.type']
            types = env_type.sudo().search([('id','=',type_id)])
            type = types[0]
            number =  type.number + 1
            trans_data = {}
            trans_data.update({'number': number})
            type.sudo().write(trans_data)
            env_trans = http.request.env['queue.trans']
            trans_data = {}        
            str_number = str(number)
            if len(str_number) == 1:
                str_number = '00' + str_number
            elif len(str_number) == 2 :
                str_number = '0' + str_number       
            trans_data.update({'trans_id': str_number})
            trans_data.update({'type_id': type_id})
            trans = env_trans.sudo().create(trans_data)                
            return '{"success":true,"message":"Transaction Process Successfully","trans_id":' + str(trans.id) + '}'
        except:
            return '{"success":false,"message":"Error"}'
        
    @http.route('/queue/appprint/', auth='public')
    def appprint(self, **kw):
        env_trans_print = http.request.env['queue.trans.print']
        transs = env_trans_print.sudo().search([('state','=','open')])
        if transs:
            trans = transs[0]
            trans_data = {}
            trans_data.update({'state': 'done'})
            trans.sudo().write(trans_data)            
            return '{"success":true,"message":"","trans_id":"' + trans.trans_id.trans_id + '"}'
        else:
            return '{"success":false,"message":"No Print Data"}'

    @http.route('/queue/kiosk', auth='public')
    def queue_kiosk(self, **kw):
        return request.render('jakc_queue.kioskscreen', {})
