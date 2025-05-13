# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import requests
import json
import logging
from odoo import fields

_logger = logging.getLogger(__name__)

class Talde3Controller(http.Controller):

    @http.route('/talde3/actualizar_datos', auth='user', type='http', website=True)
    def actualizar_datos(self, **kw):
        try:
            api_url = 'http://192.168.115.154/api.php'
            endpoints = [
                'zerbitzaria',
                'mahaia',
                'platera',
                'eskaera',
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
                    _logger.debug(f"Respuesta cruda de {endpoint}: {response.text}")
                    data = response.json()
                    if isinstance(data, dict) and 'error' in data:
                        error_msg = f"{endpoint}: error en API: {data['error']}"
                        _logger.error(error_msg)
                        errores.append(error_msg)
                        continue
                    self.actualizar_tabla(endpoint, data)
                    request.env.cr.commit()
                except requests.exceptions.RequestException as e:
                    error_msg = f"{endpoint}: error de conexión: {str(e)}"
                    _logger.error(error_msg)
                    errores.append(error_msg)
                    request.env.cr.rollback()
                except json.JSONDecodeError as e:
                    error_msg = f"{endpoint}: respuesta no válida (no es JSON): {response.text}"
                    _logger.error(error_msg)
                    errores.append(error_msg)
                    request.env.cr.rollback()
                except Exception as e:
                    error_msg = f"{endpoint}: error al procesar: {str(e)}"
                    _logger.error(error_msg)
                    errores.append(error_msg)
                    request.env.cr.rollback()

            if errores:
                return http.Response(
                    '<html><body><h1>Error</h1><p>Fallaron los siguientes endpoints:</p><ul>' +
                    ''.join(f'<li>{e}</li>' for e in errores) +
                    '</ul><a href="/web">Volver</a></body></html>',
                    content_type='text/html'
                )
            else:
                return request.redirect('/web#action=%s' % request.env.ref('talde3.action_eskaera_platera').id)

        except Exception as e:
            _logger.error(f"Error crítico: {str(e)}", exc_info=True)
            request.env.cr.rollback()
            return http.Response(
                '<html><body><h1>Error Crítico</h1><p>No se pudieron actualizar los datos. Detalles: ' +
                str(e) + '</p><a href="/web">Volver</a></body></html>',
                content_type='text/html'
            )

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
            elif endpoint == 'zerbitzaria':
                request.env['talde3.zerbitzaria'].sudo().search([]).unlink()
                for item in data:
                    self.actualizar_zerbitzaria(item)
            elif endpoint == 'mahaia':
                # Delete dependent eskaera records first to avoid foreign key violation
                request.env['talde3.eskaera'].sudo().search([]).unlink()
                request.env['talde3.mahaia'].sudo().search([]).unlink()
                for item in data:
                    self.actualizar_mahaia(item)
            elif endpoint == 'eskaera':
                request.env['talde3.eskaera'].sudo().search([]).unlink()
                for item in data:
                    self.actualizar_eskaera(item)
            elif endpoint == 'platera':
                request.env['talde3.platera'].sudo().search([]).unlink()
                for item in data:
                    self.actualizar_platera(item)

    def actualizar_eskaera_zerbitzaria(self, item):
        if not item.get('Platera') or not item.get('Eskaera_guztiak'):
            _logger.warning(f"Datos incompletos para eskaera.zerbitzaria: {item}")
            return
        request.env['eskaera.zerbitzaria'].sudo().create({
            'platera': item['Platera'],
            'eskaera_guztiak': int(item['Eskaera_guztiak'])
        })

    def actualizar_eskaera_platera(self, item):
        if not item.get('Zerbitzaria') or not item.get('Eskaera_guztiak'):
            _logger.warning(f"Datos incompletos para eskaera.platera: {item}")
            return
        request.env['eskaera.platera'].sudo().create({
            'zerbitzaria': item['Zerbitzaria'],
            'eskaera_guztiak': int(item['Eskaera_guztiak'])
        })

    def actualizar_eskaera_eguna_astero(self, item):
        if not item.get('dia_semana') or not item.get('total_pedidos'):
            _logger.warning(f"Datos incompletos para eskaera.eguna_astero: {item}")
            return
        request.env['eskaera.eguna_astero'].sudo().search([]).unlink()
        request.env['eskaera.eguna_astero'].sudo().create({
            'dia_semana': item['dia_semana'],
            'total_pedidos': int(item['total_pedidos'])
        })

    def actualizar_faktura_egunero_astero(self, item):
        if not item.get('dia_semana') or not item.get('total_facturas'):
            _logger.warning(f"Datos incompletos para faktura.egunero_astero: {item}")
            return
        request.env['faktura.egunero_astero'].sudo().search([]).unlink()
        request.env['faktura.egunero_astero'].sudo().create({
            'dia_semana': item['dia_semana'],
            'total_facturas': int(item['total_facturas'])
        })

    def actualizar_eskaerak_egunero_hilero(self, item):
        if not item.get('dia_mes') or item.get('dia_mes') == '0' or not item.get('total_pedidos'):
            _logger.warning(f"Datos incompletos o inválidos para eskaerak.egunero_hilero: {item}")
            return
        try:
            dia_mes = str(int(item['dia_mes']))  # Ensure dia_mes is a valid integer string
            if int(dia_mes) < 1 or int(dia_mes) > 31:
                _logger.warning(f"Valor inválido para dia_mes: {dia_mes}")
                return
            request.env['eskaerak.egunero_hilero'].sudo().search([]).unlink()
            request.env['eskaerak.egunero_hilero'].sudo().create({
                'dia_mes': dia_mes,
                'total_pedidos': int(item['total_pedidos'])
            })
        except (ValueError, TypeError) as e:
            _logger.error(f"Error procesando dia_mes para eskaerak.egunero_hilero: {item}, error: {str(e)}")
            raise

    def actualizar_zerbitzaria(self, item):
        if not item.get('dni') or not item.get('izena') or not item.get('abizena'):
            _logger.warning(f"Datos incompletos para talde3.zerbitzaria: {item}")
            return
        try:
            request.env['talde3.zerbitzaria'].sudo().create({
                'dni': item['dni'],
                'izena': item['izena'],
                'abizena': item['abizena'],
                'pasahitza': item.get('pasahitza', ''),
                'korreoa': item.get('korreoa', ''),
                'telefonoa': item.get('telefonoa', ''),
                'postua': item.get('postua', ''),
                'txat_baimena': item.get('txat_baimena') in [1, '1', True, 'true', 'True']
            })
        except Exception as e:
            _logger.error(f"Error creando zerbitzaria {item.get('dni', 'desconocido')}: {str(e)}")
            raise

    def actualizar_mahaia(self, item):
        if not item.get('mahaiZenbakia'):
            _logger.warning(f"Datos incompletos para talde3.mahaia: {item}")
            return
        try:
            request.env['talde3.mahaia'].sudo().create({
                'mahai_zenbakia': int(item['mahaiZenbakia']),
                'kopurua': int(item.get('kopurua', 0)),
                'habilitado': bool(item.get('habilitado', True))
            })
        except Exception as e:
            _logger.error(f"Error creando mahaia {item.get('mahaiZenbakia', 'desconocido')}: {str(e)}")
            raise

    def actualizar_eskaera(self, item):
        if not item.get('eskaera_zenb') or not item.get('izena') or not item.get('mesa_id'):
            _logger.warning(f"Datos incompletos para talde3.eskaera: {item}")
            return
        try:
            mesa = request.env['talde3.mahaia'].sudo().search([('mahai_zenbakia', '=', int(item['mesa_id']))], limit=1)
            if not mesa:
                _logger.warning(f"Mesa {item['mesa_id']} no encontrada para eskaera {item['eskaera_zenb']}")
                return
            request.env['talde3.eskaera'].sudo().create({
                'eskaera_zenb': int(item['eskaera_zenb']),
                'izena': item['izena'],
                'prezioa': float(item.get('prezioa', 0.0)),
                'mesa_id': mesa.id
            })
        except Exception as e:
            _logger.error(f"Error creando eskaera {item.get('eskaera_zenb', 'desconocido')}: {str(e)}")
            raise

    def actualizar_platera(self, item):
        if not item.get('izena'):
            _logger.warning(f"Datos incompletos para talde3.platera: {item}")
            return
        try:
            created_by = item.get('createdBy')
            if created_by:
                user = request.env['res.users'].sudo().search([('id', '=', int(created_by))], limit=1)
                created_by = user.id if user else request.env.user.id
            else:
                created_by = request.env.user.id
            request.env['talde3.platera'].sudo().create({
                'izena': item['izena'],
                'deskribapena': item.get('deskribapena', ''),
                'kategoria': item.get('kategoria', ''),
                'menu': bool(item.get('menu', False)),
                'created_at': item.get('createdAt') or fields.Datetime.now(),
                'created_by': created_by
            })
        except Exception as e:
            _logger.error(f"Error creando platera {item.get('izena', 'desconocido')}: {str(e)}")
            raise