# Classes for receiving and sending messages
import falcon, json
from ..storage import connection

import time, io, datetime
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

def message_to_dict(message: connection.Message, session, individual=False):
    unix_time = time.mktime(message.date.timetuple())
    message_dict = dict()
    message_dict['message id'] = message.id
    message_dict['partner id'] = message.partner_id
    message_dict['template id'] = message.template_type
    message_dict['interchange control number'] = message.get_interchange_container(session).control_number
    if message.group_id:
        message_dict['group control number'] = message.group.control_number
    message_dict['transaction control number'] = message.control_number
    message_dict['date'] = unix_time
    message_dict['status'] = message.status.value
    if individual:
        template = message.get_template()
        message_dict['content'] = template.get_detailed_content()
    return message_dict

class Messages:

    # Get method returns all message descriptions
    def on_get(self, req, resp):
        messages = self.session.query(connection.Message).order_by(connection.Message.date.desc()).all()
        out_list = list()

        for message in messages:
            tmp_dict = message_to_dict(message, self.session)
            out_list.append(tmp_dict)

        resp.body = json.dumps(out_list, indent=2)

    # Submit EDI file

    def on_put(self, req:falcon.request.Request, resp):

        #self.conf = config.File()

        # First version of receiving edi files. Only one file at a time is currently supported
        # TODO: Add integrity checking
        def ver_zero():
            target_temp = None

            # Discover matching template
            for template in stream_handle.template_operators.template_list:
                if req.media['template id'] == template.identifier_code:
                    target_temp = template
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
            id_tuple = edi_obj.get_id_tuple(template)


            # Create New Message and Container
            interchange_container = connection.InterchangeContainer()
            interchange_container.partner_id = int(req.media['partner id'])
            interchange_container.content = edi_obj.ISA.get_bytes_list()
            interchange_container.control_number = id_tuple[0]

            self.session.add(interchange_container)
            self.session.commit()

            if template.GS:
                group_container = connection.GroupContainer()
                group_container.partner_id = int(req.media['partner id'])
                group_container.interchange_id = interchange_container.id
                group_container.content = template.GS.get_bytes_list()
                group_container.control_number = id_tuple[1]

                self.session.add(group_container)
                self.session.commit()

            new_message = connection.Message()
            new_message.partner_id = int(req.media['partner id'])
            new_message.template_type = int(template.template_type)
            new_message.interchange_id = interchange_container.id
            if template.GS:
                new_message.group_id = group_container.id
            new_message.content = template.get_bytes_list()
            new_message.date = datetime.datetime.now()
            new_message.control_number = id_tuple[2]
            new_message.status = connection.Status.send

            self.session.add(new_message)
            self.session.commit()

        if req.media['content version'] == 0:
            ver_zero()


class Message:

    def on_get(self, req, resp, message_id):
        message = self.session.query(connection.Message).filter_by(id=message_id).first()
        out_dict = message_to_dict(message, self.session, individual=True)

        resp.body = json.dumps(out_dict, indent=2)


