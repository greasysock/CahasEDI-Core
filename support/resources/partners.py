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

def partner_upload(partner: Partnership, message: bytes):
    delimiter = message[3:4]
    line_separator = message.split(delimiter)[16][1:2]
    
    processed_list = list()
    for section in message.split(line_separator):
        processed_list.append(section.split(delimiter))
    print(processed_list)

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

class PartnerUpload:

    def on_put(self, req, resp, partner_id):
        partner = self.session.query(Partnership).filter_by(id=partner_id).first()
        if req.content_type == 'application/octet-stream' and partner:
            partner_upload
            content = req.stream.read()
            delimiter = content[3:4]
            line_separator = content.split(delimiter)[16][1:2]
            
            processed_list = list()
            for section in content.split(line_separator):
                processed_list.append(section.split(delimiter))
            print(processed_list)