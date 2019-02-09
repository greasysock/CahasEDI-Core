from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime, PickleType, Enum, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .. import config
from sqlalchemy.orm import sessionmaker
import enum

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

    def get_interchange_counter(self):
        self.interchange_counter += 1
        return self.interchange_counter

    def get_group_counter(self):
        self.group_counter += 1
        return self.group_counter

    def get_set_counter(self):
        self.set_counter += 1
        return self.set_counter


class Acknowledge(Base):

    __tablename__ = "acknowledge"

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, nullable=False)
    ack_content = Column(PickleType, nullable=True)
    status = Column(Enum(Status), nullable=True)
    interchange_control_number = Column(Integer, nullable=False)


class Message(Base):

    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, nullable=False)
    template_type = Column(Integer, nullable=False)
    interchange_control_number = Column(Integer, nullable=False)
    group_control_number = Column(Integer)
    transaction_control_number = Column(Integer, nullable=False)
    acknowledge_id = Column(Integer)
    content = Column(PickleType, nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(Enum(Status), nullable=False)


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
    engine = create_engine('postgresql://{}:{}@localhost:5432/{}'.format(conf.db_login, conf.db_password, conf.db_name))
    Base.metadata.create_all(engine)
    check_partner_health(engine, conf)
    return engine
