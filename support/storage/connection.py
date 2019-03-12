from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime, PickleType, Enum, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .. import config
from ..edi import stream_handle
from sqlalchemy.orm import sessionmaker
import enum, datetime

Base = declarative_base()


class Status(enum.Enum):

    # Messages from Partner
    received = 0

    # Messages to Partner
    send = 2
    sent = 3

    # Status for both send/receive
    acknowledged_na = 5
    acknowledged = 6
    acknowledged_fail = 7


class Partnership(Base):

    __tablename__ = "partnership"

    id = Column(Integer, primary_key=True)
    partner_name = Column(String(250), nullable=False, unique=True)
    partner_logo = Column(LargeBinary)
    interchange_id = Column(String(15), nullable=False, unique=True)
    interchange_qualifier = Column(String(2), nullable=False)

    interchange_counter = Column(Integer)
    group_counter = Column(Integer)
    set_counter = Column(Integer)

    watch_dir = Column(String(250), nullable=False, unique=True)
    send_dir = Column(String(250), nullable=False, unique=True)
    last_check = Column(DateTime)

    messages = relationship("Message", backref="partner")

    def update_timestamp(self):
        self.last_check = datetime.datetime.now()

    def get_interchange_counter(self):
        if self.interchange_counter or self.group_counter == 0:
            self.interchange_counter += 1
        else:
            self.interchange_counter = 0
        return self.interchange_counter

    def get_group_counter(self):
        if self.group_counter or self.group_counter == 0:
            self.group_counter += 1
        else:
            self.group_counter = 0
        return self.group_counter

    def get_set_counter(self):
        if self.set_counter or self.set_counter == 0:
            self.set_counter += 1
        else:
            self.set_counter = 0
        return self.set_counter


class Acknowledge(Base):

    __tablename__ = "acknowledge"

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, nullable=False)
    ack_content = Column(PickleType, nullable=True)
    status = Column(Enum(Status), nullable=True)
    interchange_id = Column(Integer, ForeignKey('interchange_container.id'), nullable=False)

# Container for building files later
class InterchangeContainer(Base):

    __tablename__ = "interchange_container"

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partnership.id') ,nullable=False)
    content = Column(PickleType, nullable=False)
    control_number = Column(Integer, nullable=False)

    groups = relationship("GroupContainer", backref="interchange")
    messages = relationship("Message", backref="interchange")
    acknowledge = relationship("Acknowledge", uselist=False)

    def get_iea(self):
        return [
            b'IEA',
            b'1',
            str(self.control_number).encode()
        ]

class GroupContainer(Base):

    __tablename__ = "group_container"

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partnership.id') ,nullable=False)
    interchange_id = Column(Integer, ForeignKey('interchange_container.id'),nullable=False)
    content = Column(PickleType, nullable=False)
    control_number = Column(Integer, nullable=False)

    messages = relationship("Message", backref="group")

    def get_ge(self):
        return [
            b'GE',
            b'1',
            str(self.control_number).encode()
        ]

class Message(Base):

    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partnership.id'), nullable=False)
    interchange_id = Column(Integer, ForeignKey('interchange_container.id'),nullable=False)
    group_id = Column(Integer, ForeignKey('group_container.id'))
    template_type = Column(Integer, nullable=False)
    control_number = Column(Integer, nullable=False)
    content = Column(PickleType, nullable=False)
    content_id = Column(String(50))
    content_parents = relationship("ContentParent", backref="message")
    date = Column(DateTime, nullable=False)
    status = Column(Enum(Status), nullable=False)

    def get_group_container(self, session):
        if self.group_id:
            return session.query(GroupContainer).filter_by(id=self.group_id).first() # type: GroupContainer

    def get_interchange_container(self, session):
        return session.query(InterchangeContainer).filter_by(id=self.interchange_id).first() # type: InterchangeContainer

    # Builds template file for message
    def get_template(self):
        target_template = None
        for template in stream_handle.template_operators.template_list:
            if template.identifier_code == self.template_type:
                target_template = template
        return target_template.get_template()(self.content)

    # Builds entire message including group and header into EdiHeader
    def get_full_file(self, session):
        interchange = self.get_interchange_container(session)  # type: InterchangeContainer
        group = self.get_group_container(session) # type: GroupContainer

        edi_array = [interchange.content] + [group.content] + self.content + [group.get_ge()] + [interchange.get_iea()]
        return stream_handle.EdiHeader(edi_array)


class ContentParent(Base):
    __tablename__ = "content_parent"
    id = Column(Integer, primary_key=True)
    parent_id = Column(String(50), nullable=False)
    partner_id = Column(Integer, nullable=False)
    message_id = Column(Integer, ForeignKey('message.id'), nullable=False)


# Checks partnerships in conf file against database, updates database when needed.
# TODO: Pretty archaic, will add api later on
def check_partner_health(engine, conf: config.File):
    Session = sessionmaker(bind=engine)
    session = Session()
    partners = session.query(Partnership).all()

    # Determines if no partners have been uploaded to sql
    if partners == []:
        for p in conf.get_partners():
            new_partner = Partnership(partner_name=p.name,
                                      interchange_id=p.id,
                                      interchange_qualifier=p.id_qualifier,
                                      watch_dir=p.watch_dir,
                                      send_dir=p.send_dir)
            session.add(new_partner)
        session.commit()
    # TODO: check partnership integrity


# Create db connection and initialize tables. TODO: Change engine depending on type
def connect(conf : config.File, type):
    engine = create_engine('postgresql://{}:{}@localhost:5432/{}'.format(conf.db_login, conf.db_password, conf.db_name), echo=True)
    Base.metadata.create_all(engine)
    check_partner_health(engine, conf)
    return engine
