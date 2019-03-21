import falcon
from support.storage import connection
import math, json, time

def page(session, page:int, page_length=20):
    start_index = (page - 1)*page_length
    return session.query(connection.Message).filter_by(template_type=810).order_by(connection.Message.date.desc()).limit(page_length).offset(start_index)

def pages(session, page_length=20):
    return math.ceil(float(session.query(connection.Message).count())/float(page_length))

def invoice_to_dict(message: connection.Message, individual=False):
    unix_time = time.mktime(message.date.timetuple())
    message_dict = dict()
    message_dict['message id'] = message.id
    message_dict['partner id'] = message.partner_id
    message_dict['template id'] = message.template_type
    message_dict['invoice id'] = message.content_id
    message_dict['related documents'] = [ {'document id' : doc.parent_id} for doc in message.content_parents ]
    message_dict['interchange control number'] = message.interchange.control_number
    if message.group_id:
        message_dict['group control number'] = message.group.control_number
    else:
        message_dict['group control number'] = None
    if message.interchange.acknowledge:
        message_dict['acknowledge status'] = message.interchange.acknowledge.status.value
    else:
        message_dict['acknowledge status'] = connection.Status.acknowledged_na.value
    message_dict['transaction control number'] = message.control_number
    message_dict['date'] = unix_time
    message_dict['status'] = message.status.value
    if individual:
        template = message.get_template()
        message_dict['content'] = template.get_detailed_content()
        message_dict['invoice'] = template.get_custom_detailed_content()
    return message_dict

class Invoices:
    page_length = 20
    def on_get(self, req, resp):

        cur_page = 1
        # Check if page param was given, otherwise return first page.
        if req.params.get('page'):
            cur_page = int(req.params['page'])
        messages = page(self.session, cur_page, page_length=self.page_length)

        out_list = list()
        for message in messages:
            tmp_dict = invoice_to_dict(message)
            out_list.append(tmp_dict)

        resp.body = json.dumps(out_list, indent=2)
        resp.set_header('X-Pages', pages(self.session, page_length=self.page_length))
        resp.set_header('X-Page', cur_page)


        pass

class Invoice:
    def on_get(self, req, resp, invoice_id):
        invoice = self.session.query(connection.Message).filter_by(id=invoice_id).first()
        resp.body = json.dumps(invoice_to_dict(invoice, individual=True))