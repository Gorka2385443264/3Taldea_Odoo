from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)

class EskaeraPlatera(models.Model):
    _name = 'eskaera.platera'
    _description = 'Eskaera Platera'

    zerbitzaria = fields.Char(string='Zerbitzaria')
    eskaera_guztiak = fields.Integer(string='Eskaera Guztiak')

    @api.model
    def create(self, vals):
        record = super(EskaeraPlatera, self).create(vals)

        try:
            payload = {
                'endpoint': 'insert_pedido_platera',
                'zerbitzaria': vals.get('zerbitzaria'),
                'eskaera_guztiak': vals.get('eskaera_guztiak')
            }
            requests.post('http://host.docker.internal/api.php', json=payload, timeout=5)
        except Exception as e:
            _logger.error(f"Error al enviar datos a API (platera): {str(e)}")

        return record

class EskaeraZerbitzaria(models.Model):
    _name = 'eskaera.zerbitzaria'
    _description = 'Eskaera Zerbitzaria'

    platera = fields.Char(string='Platera')
    eskaera_guztiak = fields.Integer(string='Eskaera Guztiak')

    @api.model
    def create(self, vals):
        record = super(EskaeraZerbitzaria, self).create(vals)

        try:
            payload = {
                'endpoint': 'insert_pedido_zerbitzaria',
                'platera': vals.get('platera'),
                'eskaera_guztiak': vals.get('eskaera_guztiak')
            }
            requests.post('http://host.docker.internal/api.php', json=payload, timeout=5)
        except Exception as e:
            _logger.error(f"Error al enviar datos a API (zerbitzaria): {str(e)}")

        return record

class EskaeraEgunaAstero(models.Model):
    _name = 'eskaera.eguna_astero'
    _description = 'Eskaera Eguna Astero'

    dia_semana = fields.Char(string='Día de la Semana')
    total_pedidos = fields.Integer(string='Total Pedidos')

    @api.model
    def create(self, vals):
        record = super(EskaeraEgunaAstero, self).create(vals)

        try:
            payload = {
                'endpoint': 'insert_eguna_astero',
                'dia_semana': vals.get('dia_semana'),
                'total_pedidos': vals.get('total_pedidos')
            }
            requests.post('http://host.docker.internal/api.php', json=payload, timeout=5)
        except Exception as e:
            _logger.error(f"Error al enviar datos a API (eguna astero): {str(e)}")

        return record

class FakturaEguneroAstero(models.Model):
    _name = 'faktura.egunero_astero'
    _description = 'Faktura Egunero Astero'

    dia_semana = fields.Char(string='Día de la Semana')
    total_facturas = fields.Integer(string='Total Facturas')

    @api.model
    def create(self, vals):
        record = super(FakturaEguneroAstero, self).create(vals)

        try:
            payload = {
                'endpoint': 'insert_faktura_astero',
                'dia_semana': vals.get('dia_semana'),
                'total_facturas': vals.get('total_facturas')
            }
            requests.post('http://host.docker.internal/api.php', json=payload, timeout=5)
        except Exception as e:
            _logger.error(f"Error al enviar datos a API (faktura astero): {str(e)}")

        return record

class EskaerakEguneroHilero(models.Model):
    _name = 'eskaerak.egunero_hilero'
    _description = 'Eskaerak Egunero Hilero'

    dia_mes = fields.Char(string='Día del Mes')
    total_pedidos = fields.Integer(string='Total Pedidos')

    @api.model
    def create(self, vals):
        record = super(EskaerakEguneroHilero, self).create(vals)

        try:
            payload = {
                'endpoint': 'insert_egunero_hilero',
                'dia_mes': vals.get('dia_mes'),
                'total_pedidos': vals.get('total_pedidos')
            }
            requests.post('http://host.docker.internal/api.php', json=payload, timeout=5)
        except Exception as e:
            _logger.error(f"Error al enviar datos a API (egunero hilero): {str(e)}")

        return record

class Zerbitzaria(models.Model):
    _name = 'talde3.zerbitzaria'
    _description = 'Zerbitzaria'

    dni = fields.Char(string='DNI', required=True)
    izena = fields.Char(string='Izena', required=True)
    abizena = fields.Char(string='Abizena', required=True)
    pasahitza = fields.Char(string='Pasahitza')
    korreoa = fields.Char(string='Korreoa')
    telefonoa = fields.Char(string='Telefonoa')
    postua = fields.Char(string='Postua')
    txat_baimena = fields.Boolean(string='Txat Baimena')

class Mahaia(models.Model):
    _name = 'talde3.mahaia'
    _description = 'Mahaia'

    mahai_zenbakia = fields.Integer(string='Mahai Zenbakia', required=True)
    kopurua = fields.Integer(string='Kopurua')
    habilitado = fields.Boolean(string='Habilitado', default=True)

class Eskaera(models.Model):
    _name = 'talde3.eskaera'
    _description = 'Eskaera'

    eskaera_zenb = fields.Integer(string='Eskaera Zenbakia', required=True)
    izena = fields.Char(string='Izena', required=True)
    prezioa = fields.Float(string='Prezioa')
    mesa_id = fields.Many2one('talde3.mahaia', string='Mahaia', required=True)

class Platera(models.Model):
    _name = 'talde3.platera'
    _description = 'Platera'

    izena = fields.Char(string='Izena', required=True)
    deskribapena = fields.Text(string='Deskribapena')
    kategoria = fields.Char(string='Kategoria')
    menu = fields.Boolean(string='Menu')
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now)
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)