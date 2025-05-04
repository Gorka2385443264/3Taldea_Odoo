# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class Talde3Controller(http.Controller):

    @http.route('/talde3/actualizar_datos', auth='user', type='http', website=True)
    def actualizar_datos(self, **kw):
        try:
            api_url = 'http://192.168.115.154/api.php'  
            endpoints = [
                'pedidos_por_servidor',
                'pedidos_por_plato',
                'dia_semana_mas_pedidos',
                'dia_semana_mas_facturas',
                'dia_mes_mas_pedidos'
            ]

            errores = []

            for endpoint in endpoints:
                try:
                    _logger.info(f"Solicitando datos de {endpoint}...")
                    response = requests.get(f"{api_url}?endpoint={endpoint}", timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    self.actualizar_tabla(endpoint, data)
                except requests.exceptions.RequestException as e:
                    error_msg = f"{endpoint}: error de conexión: {str(e)}"
                    _logger.error(error_msg)
                    errores.append(error_msg)
                except json.JSONDecodeError:
                    error_msg = f"{endpoint}: respuesta no válida (no es JSON)"
                    _logger.error(error_msg)
                    errores.append(error_msg)
                except Exception as e:
                    error_msg = f"{endpoint}: error inesperado: {str(e)}"
                    _logger.error(error_msg)
                    errores.append(error_msg)

            if errores:
                return request.render('talde3.error_template', {
                    'error': 'Fallaron los siguientes endpoints:<br>' + '<br>'.join(errores)
                })
            else:
                return request.redirect('/web#action=%s' % request.env.ref('talde3.action_eskaera_platera').id)

        except Exception as e:
            _logger.error(f"Error crítico: {str(e)}", exc_info=True)
            return request.render('talde3.error_template', {
                'error': f"No se pudieron actualizar los datos. Detalles: {str(e)}"
            })

    def actualizar_tabla(self, endpoint, data):
        if endpoint in ['dia_semana_mas_pedidos', 'dia_semana_mas_facturas', 'dia_mes_mas_pedidos']:
            if data:
                if endpoint == 'dia_semana_mas_pedidos':
                    self.actualizar_eskaera_eguna_astero(data)
                elif endpoint == 'dia_semana_mas_facturas':
                    self.actualizar_faktura_egunero_astero(data)
                elif endpoint == 'dia_mes_mas_pedidos':
                    self.actualizar_eskaerak_egunero_hilero(data)
        else:
            if endpoint == 'pedidos_por_servidor':
                request.env['eskaera.platera'].sudo().search([]).unlink()
                for item in data:
                    self.actualizar_eskaera_platera(item)
            elif endpoint == 'pedidos_por_plato':
                request.env['eskaera.zerbitzaria'].sudo().search([]).unlink()
                for item in data:
                    self.actualizar_eskaera_zerbitzaria(item)

    def actualizar_eskaera_zerbitzaria(self, item):
        request.env['eskaera.zerbitzaria'].sudo().create({
            'platera': item['Platera'],
            'eskaera_guztiak': int(item['Eskaera_guztiak'])
        })

    def actualizar_eskaera_platera(self, item):
        request.env['eskaera.platera'].sudo().create({
            'zerbitzaria': item['Zerbitzaria'],
            'eskaera_guztiak': int(item['Eskaera_guztiak'])
        })

    def actualizar_eskaera_eguna_astero(self, item):
        request.env['eskaera.eguna_astero'].sudo().search([]).unlink()
        request.env['eskaera.eguna_astero'].sudo().create({
            'dia_semana': item['dia_semana'],
            'total_pedidos': int(item['total_pedidos'])
        })

    def actualizar_faktura_egunero_astero(self, item):
        request.env['faktura.egunero_astero'].sudo().search([]).unlink()
        request.env['faktura.egunero_astero'].sudo().create({
            'dia_semana': item['dia_semana'],
            'total_facturas': int(item['total_facturas'])
        })

    def actualizar_eskaerak_egunero_hilero(self, item):
        request.env['eskaerak.egunero_hilero'].sudo().search([]).unlink()
        request.env['eskaerak.egunero_hilero'].sudo().create({
            'dia_mes': str(item['dia_mes']),
            'total_pedidos': int(item['total_pedidos'])
        })
