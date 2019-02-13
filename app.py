from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from support import config
import falcon
from support.resources import messages, partners, templates
from support.storage import connection

conf = config.File("config.json")

engine = connection.connect(conf, 'postgresql')

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class SQLAlchemySessionManager:
    """
    Create a scoped session for every request and close it when the request
    ends.
    """

    def __init__(self, Session):
        self.Session = Session

    def process_resource(self, req, resp, resource, params):
        resource.session = self.Session()

    def process_response(self, req, resp, resource, req_succeeded):
        if hasattr(resource, 'session'):
            Session.remove()


class ConfSessionManager:
    """
    Create a scoped session for conf resource
    """

    def __init__(self, conf: config.File):
        self.conf = conf

    def process_resource(self, req, resp, resource, params):
        resource.conf = self.conf

    def process_response(self, req, resp, resource, req_succeeded):
        if hasattr(resource, 'conf'):
            resource.conf = None



app = falcon.API(middleware=[
    SQLAlchemySessionManager(Session),
    ConfSessionManager(conf)
])

local_messages = messages.Messages()
local_message = messages.Message()
local_partners = partners.Partners()
local_partner = partners.Partner()
local_templates = templates.Templates()
local_template = templates.Template()

app.add_route('/messages', local_messages)
app.add_route('/messages/{message_id}', local_message)
app.add_route('/partners', local_partners)
app.add_route('/partners/{partner_id}', local_partner)
app.add_route('/templates', local_templates)
app.add_route('/templates/{template_id}', local_template)


