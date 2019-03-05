from ..storage.connection import Partnership
import json
from .. import config



class Partners:

    def on_get(self, req, resp):
        out_partners = list()
        partners = self.session.query(Partnership).all()
        for partner in partners:
            partner_dict = dict()
            partner_dict['id'] = partner.id
            partner_dict['name'] = partner.partner_name
            partner_dict['interchange id'] = partner.interchange_id
            partner_dict['interchange qualifier'] = partner.interchange_qualifier
            out_partners.append(partner_dict)
        resp.body = json.dumps(out_partners, indent=2)


class Partner:

    def on_get(self, req, resp, partner_id):
        partner = self.session.query(Partnership).filter_by(id=partner_id).first()
        partner_dict = dict()
        partner_dict['id'] = partner.id
        partner_dict['name'] = partner.partner_name
        partner_dict['interchange id'] = partner.interchange_id
        partner_dict['interchange qualifier'] = partner.interchange_qualifier
        resp.body = json.dumps(partner_dict, indent=2)
