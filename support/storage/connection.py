from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime, PickleType, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class Status(enum.Enum):
    received = 0
    send = 2
    sent = 3


class Partnership(Base):

    __tablename__ = "partnership"

    id = Column(Integer, primary_key=True)
    interchange_id = Column(String(15), nullable=False, unique=True)
    interchange_qualifier = Column(String(2), nullable=False)
    watch_dir = Column(String(250), nullable=False, unique=True)
    send_dir = Column(String(250), nullable=False, unique=True)


class Message(Base):

    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, nullable=False)
    template_type = Column(Integer, nullable=False)
    content = Column(PickleType, nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(Enum(Status), nullable=False)


# Create db connection and initialize tables. TODO: Change engine depending on type
def connect(user, password, database, type):
    engine = create_engine('postgresql://{}:{}@localhost:5432/{}'.format(user, password, database))
    Base.metadata.create_all(engine)

    return engine
