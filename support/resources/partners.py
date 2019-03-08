from ..storage.connection import Partnership
import json
from .. import config

def partner_to_dict(partner: Partnership):
    partner_dict = dict()
    partner_dict['id'] = partner.id
    partner_dict['name'] = partner.partner_name
    partner_dict['interchange id'] = partner.interchange_id
    partner_dict['interchange qualifier'] = partner.interchange_qualifier
    return partner_dict

class Partners:

    def on_get(self, req, resp):
        out_partners = list()
        partners = self.session.query(Partnership).all()
        for partner in partners:
            out_partners.append(partner_to_dict(partner))
        resp.body = json.dumps(out_partners, indent=2)

class Partner:

    def on_get(self, req, resp, partner_id):
        partner = self.session.query(Partnership).filter_by(id=partner_id).first()
        partner_dict = partner_to_dict(partner)
        resp.body = json.dumps(partner_dict, indent=2)
