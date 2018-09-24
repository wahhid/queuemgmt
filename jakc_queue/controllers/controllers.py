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
            return request.render('jakc_queue.pickupscreen', {'pickup': pickup_data, })

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
                trans_id.write({'state': 'open', 'type_id': pickup.type_id.id, 'pickup_id': pickup.id})
                trans_data = {}
                trans_data.update({'id': trans_id.id})
                trans_data.update({'trans_id': trans_id.trans_id})
                trans_data.update({'type_id': trans_id.type_id.id})
                trans_data.update({'type_name': trans_id.type_id.name})
                return json.dumps(trans_data)
            else:
                return '{"success":false,"message":"No Queue"}'
        else:
            return '{"success":false,"message":"No Queue"}'


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
        pickup_log_args = [('state', '=', 'opened')]
        pickup_list = []
        pickup_log_ids = queue_pickup_log_obj.search_read(pickup_log_args)
        for pickup_log_id in pickup_log_ids:
            pickup_id = queue_pickup_obj.browse(pickup_log_id['pickup_id'][0])
            if pickup_id.display_id['id'] == display_id:
                pickup_data = {}
                pickup_data.update({'pickup_name': pickup_id['name']})
                pickup_data.update({'counter_name': pickup_id.type_id['name']})
                pickup_data.update({'current_trans': '202'})
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
            trans_data.update({'current_trans': '202'})
            trans_data.update({'counter_fa': 'fa-users'})
            trans_data.update({'counter_code': '0001'})
            type_id = queue_type_obj.browse(trans_id.type_id.id)
            trans_data.update({'counter_bg': type_id.bg_color})
            trans_list.append(trans_data)
        return json.dumps(trans_list)


class Queue(http.Controller):
    @http.route('/queue/queue/<int:id>', auth='public')
    def index(self, id, **kw):
        Types = http.request.env['queue.type']
        return http.request.render('jakc_queue.index', {
            'types': Types.search([('id','=', id)])
        })


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

    @http.route('/pos/appprint/receipt/<int:id>', type='http', auth='user')
    def print_sale_details(self, id, **kw):
        r = request.env['report.point_of_sale.report_saledetails']
        pdf = request.env['report'].with_context(id=id).get_pdf(r, 'point_of_sale.report_saledetails')
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

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
        queue_type = http.request.env['queue.type']
        type_ids = queue_type.search([])
        for type in type_ids:
            type.mod_bg_color = 'btn3d btn ' + type.bg_color + ' btn-lg btn-block'
        return request.render('jakc_queue.kioskscreen', {'types': type_ids})
