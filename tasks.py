import support.config as config
from support.edi import stream_handle
import support.storage.connection as connection
from support.storage.connection import Partnership, Message, Status, Acknowledge, InterchangeContainer, GroupContainer
from sqlalchemy.orm import sessionmaker
import os, datetime, io
from support.edi.templates import generic, x12_997
from huey import crontab
from support.task_conf import huey

config_file = "config.json"

conf = config.File(config_file)
db = connection.connect(conf, "postgresql")
Session = sessionmaker(bind=db)

# Check for incoming edi files and return binary list of accepted files
def check_watch_dir(watch_dir: str, time):
    out_edis = list()

    files = os.listdir(watch_dir)
    for file in files:
        f = watch_dir + "/" + file
        t = os.path.getctime(f)
        t = datetime.datetime.fromtimestamp(t)
        if t > time:
            bytesfile = io.BytesIO()
            with open(f, "rb") as raw:
                bytesfile.writelines(raw.readlines())
            bytesfile.seek(0)
            edi_file = stream_handle.EdiFile(bytesfile)
            out_edis.append(edi_file)
    return out_edis

def update_timestamp(partner:Partnership):
    ses = Session()
    target = ses.query(Partnership).filter_by(id=partner.id).first()
    target.last_check = datetime.datetime.now()
    ses.commit()
    ses.close()
    return target

# Check partner directories for incoming EDI files
@huey.periodic_task(crontab(minute='*'))
def partner_directory_check():
    session = Session()
    partners = session.query(Partnership).all()
    for partner in partners:
        partner_message_check(partner)
    

def partner_message_check(partner: Partnership):
    # Check for existing timestamp
    if partner.last_check is None:
        partner = update_timestamp(partner)

    edi_objs = check_watch_dir(partner.watch_dir, partner.last_check)
    if edi_objs != []:
        update_timestamp(partner)
        for edi_obj in edi_objs:
            receive_message(edi_obj, partner)

# Adds ack to ack send queue
def prepare_ack(ackno: generic.Template, partner: Partnership):
    edi_partnership = stream_handle.PartnershipData(conf.id_qualifier, conf.id, partner.interchange_qualifier, partner.interchange_id)
    edi_partnership.set_interchange_counter_method(partner.get_interchange_counter)
    edi_partnership.set_group_counter_method(partner.get_group_counter)
    edi_partnership.set_set_counter_method(partner.get_set_counter)
    edi_head = stream_handle.EdiHeader(partner_data=edi_partnership)
    edi_head.append_template(ackno)
    return edi_head.get_all_bytes_lists()

def create_acknowledge(message: stream_handle.EdiFile, partner: Partnership):
    ack_message = Acknowledge()
    ack_message.ack_content = prepare_ack(message.edi_header.ack, partner)
    ack_message.partner_id = partner.id
    ack_message.status = Status.send
    return ack_message

# Creates interchange line in DB for incoming sections
def create_interchange_container(message: stream_handle.EdiHeader, partner: Partnership):
    interchange = InterchangeContainer()
    interchange.control_number = int(message.ISA[13])
    interchange.content = message.ISA.get_bytes_list()
    interchange.partner_id = partner.id
    return interchange

def create_group_container(group: stream_handle.EdiGroup, partner: Partnership):
    gs,ge = group.get_gs_ge()

    group_container = GroupContainer()
    group_container.content = gs.get_bytes_list()
    group_container.control_number = group.control_num
    group_container.partner_id = partner.id
    
    return group_container

def get_content_ids(content: generic.Template):

def create_message(content: generic.Template, partner: Partnership, interchange: InterchangeContainer):
    tmp_message = Message()

    tmp_message.date = datetime.datetime.now()
    tmp_message.content = content.get_bytes_list()
    tmp_message.partner_id = partner.id
    tmp_message.control_number = content.control_num
    tmp_message.template_type = content.template_type
    tmp_message.status = Status.received
    interchange.messages.append(tmp_message)
    return tmp_message

@huey.task()
def receive_message(message: stream_handle.EdiHeader, partner: Partnership):

    # Make interchange container
    interchange = create_interchange_container(message.edi_header, partner)

    # Check if only one set was received
    if message == []:
        for content in message.edi_header.get_all_content():
            msg = create_message(content, partner, interchange)
            interchange.messages.append(msg)
        return

    # Generate ACK if requested
    if message.edi_header.ack:
        ack = create_acknowledge(message, partner)
        interchange.acknowledge = ack

    # Make group container
    for group in message.edi_header: # type: stream_handle.EdiGroup
        group_container = create_group_container(group, partner)
        for content in group: # type: generic.Template
            if content.template_type == x12_997.description.identifier_code:
                pass
            else:
                message = create_message(content, partner, interchange)
                group_container.messages.append(message)
        interchange.groups.append(group_container)
    session = Session()
    session.add(interchange)
    session.commit()
    session.close()