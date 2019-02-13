# Classes for receiving and sending messages
import falcon, json
from ..storage import connection
import time, io
from support.edi import stream_handle
from .. import config


def numbered_dict_to_list(tar:dict):

    out_list = list()

    for i in range(tar.__len__()):
        tem = tar[str(i)]
        if type(tem) == dict:
            out_list.append(numbered_dict_to_list(tem))
        elif type(tem) == str:
            out_list.append(tem.encode())

    return out_list


class Messages:

    # Get method returns all message descriptions
    def on_get(self, req, resp):
        messages = self.session.query(connection.Message).all()
        out_list = list()

        for message in messages:
            unix_time = time.mktime(message.date.timetuple())
            tmp_dict = dict()
            tmp_dict['message id'] = message.id
            tmp_dict['partner id'] = message.partner_id
            tmp_dict['document type'] = message.template_type
            tmp_dict['date'] = unix_time
            tmp_dict['status'] = message.status.value
            out_list.append(tmp_dict)

        resp.body = json.dumps(out_list, indent=2)

    # Submit EDI file

    def on_put(self, req:falcon.request.Request, resp):

        #self.conf = config.File()

        # First version of receiving edi files. Only one file at a time is currently supported
        def ver_zero():
            target_temp = None

            # Discover matching template
            for template in stream_handle.template_operators.template_list:
                if req.media['template id'] == template.identifier_code:
                    target_temp = template
            print(target_temp)
            partner = self.session.query(connection.Partnership).filter_by(id=req.media['partner id']).first()
            #partner = connection.Partnership()

            # initialize partnership information and connect counter methods
            partnership = stream_handle.PartnershipData(self.conf.id_qualifier, self.conf.id, partner.interchange_qualifier, partner.interchange_id)

            partnership.set_interchange_counter_method(partner.get_interchange_counter)
            partnership.set_group_counter_method(partner.get_group_counter)
            partnership.set_set_counter_method(partner.get_set_counter)

            # Find content in message and assign to appropriate template
            content = numbered_dict_to_list(req.media['content'])
            template = target_temp.get_template()(content)

            # Build EdiHeader object and append template
            edi_obj = stream_handle.EdiHeader(partner_data=partnership)
            edi_obj.append_template(template)
            tmp_mem = io.BytesIO()
            edi_file = stream_handle.EdiFile(tmp_mem)
            edi_file.edi_header = edi_obj
            out_template = edi_file.get_open_file()
            lines = out_template.readlines()
            print(lines)


        if req.media['content version'] == 0:
            ver_zero()


class Message:

    def on_get(self, req, resp, message_id):
        message = self.session.query(connection.Message).filter_by(id=message_id).first()

        unix_time = time.mktime(message.date.timetuple())
        out_dict = dict()
        out_dict['message id'] = message.id
        out_dict['partner id'] = message.partner_id
        out_dict['template id'] = message.template_type
        out_dict['date'] = unix_time
        out_dict['status'] = message.status.value
        out_dict['content'] = message.content

        resp.body = json.dumps(out_dict, indent=2)


