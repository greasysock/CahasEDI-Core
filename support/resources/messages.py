# Classes for receiving and sending messages
import falcon, json
from ..storage import connection
import time


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

class Message:

    def on_get(self, req, resp, message_id):
        message = self.session.query(connection.Message).filter_by(id=message_id).first()

        unix_time = time.mktime(message.date.timetuple())
        out_dict = dict()
        out_dict['message id'] = message.id
        out_dict['partner id'] = message.partner_id
        out_dict['document type'] = message.template_type
        out_dict['date'] = unix_time
        out_dict['status'] = message.status.value
        out_dict['content'] = message.content

        resp.body = json.dumps(out_dict, indent=2)

    # Submit EDI file
    def on_put(self, req, resp):
        pass
