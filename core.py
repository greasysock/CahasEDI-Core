import support.config as config
from support.edi import stream_handle
import support.storage.connection as connection
from support.storage.connection import Partnership, Message, Status, Acknowledge, InterchangeContainer, GroupContainer
from sqlalchemy.orm import sessionmaker
import os, datetime, io
from support.edi.templates import generic, x12_997

config_file = "config.json"

conf = config.File(config_file)
db = connection.connect(conf, "postgresql")


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


def partner_loop(partner:Partnership):

    # Adds ack to ack send queue
    def prepare_ack(ackno: generic.Template):
        edi_partnership = stream_handle.PartnershipData(conf.id_qualifier, conf.id, partner.interchange_qualifier, partner.interchange_id)
        edi_partnership.set_interchange_counter_method(partner.get_interchange_counter)
        edi_partnership.set_group_counter_method(partner.get_group_counter)
        edi_partnership.set_set_counter_method(partner.get_set_counter)
        edi_head = stream_handle.EdiHeader(partner_data=edi_partnership)
        edi_head.append_template(ackno)
        return edi_head.get_all_bytes_lists()
    def ack_process_handle(message: stream_handle.EdiFile, interchange_id:int):
        session = Session()

        ack_message = Acknowledge()
        ack_message.interchange_id = interchange_id
        ack_message.ack_content = prepare_ack(message.edi_header.ack)
        ack_message.partner_id = partner.id
        ack_message.status = Status.send
        session.add(ack_message)
        session.commit()
        msg_id = ack_message.id
        session.close()

    def receive_message_handle(content: generic.Template, interchange_id, group_id = None):
        session = Session()

        tmp_message = Message()
        if group_id:
            tmp_message.group_id = group_id

        tmp_message.date = datetime.datetime.now()
        tmp_message.content = content.get_bytes_list()
        tmp_message.partner_id = partner.id
        tmp_message.interchange_id = interchange_id
        tmp_message.control_number = content.control_num

        tmp_message.template_type = content.template_type
        tmp_message.status = Status.received
        session.add(tmp_message)
        session.commit()
        session.close()

    # TODO
    def receive_ack_handle(content: x12_997):
        pass

    # Creates interchange line in DB for incoming sections
    def create_interchange_container(message: stream_handle.EdiHeader):
        interchange = InterchangeContainer()
        interchange.control_number = int(message.ISA[13])
        interchange.content = message.ISA.get_bytes_list()
        interchange.partner_id = partner.id

        session = Session()
        session.add(interchange)
        session.commit()
        return interchange.id

    def create_group_container(group: stream_handle.EdiGroup, interchange_id: int):
        gs,ge = group.get_gs_ge()

        group_container = GroupContainer()
        group_container.partner_id = partner.id
        group_container.content = gs.get_bytes_list()
        group_container.control_number = group.control_num
        group_container.interchange_id = interchange_id

        session = Session()
        session.add(group_container)
        session.commit()
        return group_container.id


    # Receiving end for incoming messages
    def receive_handle(message: stream_handle.EdiFile):

        # Make interchange container
        interchange_id = create_interchange_container(message.edi_header)

        # Check if only one set was received
        if message.edi_header == []:
            for content in message.edi_header.get_all_content():
                receive_message_handle(content, interchange_id)
            return

        # Generate ACK if requested
        if message.edi_header.ack:
            ack_process_handle(message, interchange_id)

        # Make group container
        for group in message.edi_header: # type: stream_handle.EdiGroup
            group_id = create_group_container(group, interchange_id)
            for content in group: # type: generic.Template
                if content.template_type == x12_997.description.identifier_code:
                    receive_ack_handle(content)
                else:
                    receive_message_handle(content, interchange_id, group_id)

    # TODO
    def message_send_handle(message: Message):
        session = Session()
        edi_head = message.get_full_file(session) # type: stream_handle.EdiHeader
        tmp = io.BytesIO()
        edi_file = stream_handle.EdiFile(tmp)
        edi_file.edi_header = edi_head
        filename = str(message.interchange_id)+ '-' + str(message.group_id)+datetime.datetime.now().strftime('-%Y%m%d-%H%M.') + 'edi'
        with open(partner.send_dir+'/'+filename, 'wb') as out_file:
            out_file.writelines(edi_file.get_open_file().readlines())

        mod_message = session.query(Message).filter_by(id=message.id).first()
        mod_message.status = Status.sent
        session.commit()


    def ack_send_handle(ack: Acknowledge):
        ediheader = stream_handle.EdiHeader(ack.ack_content)
        edi_file = io.BytesIO()
        stream = stream_handle.EdiFile(edi_file)
        stream.edi_header = ediheader
        edi_file = stream.get_open_file()
        filename = datetime.datetime.now().strftime('ACK-%Y%m%d-%H%M.') + str(ediheader.get_all_content()[0].template_type)
        with open(partner.send_dir+'/'+filename, 'wb') as out_file:
            out_file.writelines(edi_file.readlines())
        session = Session()
        new_ack = session.query(Acknowledge).filter_by(id=ack.id).first()
        new_ack.status = Status.sent
        #ack.status = Status.sent
        session.commit()
        session.close()

    # Check for existing timestamp
    if partner.last_check is None:
        partner = update_timestamp(partner)

    # Check for incoming messages
    edi_objs = check_watch_dir(partner.watch_dir, partner.last_check)
    if edi_objs != []:
        update_timestamp(partner)
        for edi_obj in edi_objs:
            receive_handle(edi_obj)

    # Check for outgoing acks
    session = Session()
    target_acks = session.query(Acknowledge).filter_by(partner_id=partner.id, status=Status.send)
    session.close()
    for ack in target_acks:
        ack_send_handle(ack)

    # Check for outgoing messages
    session = Session()
    target_messages = session.query(Message).filter_by(partner_id= partner.id, status=Status.send)
    session.close()
    for message in target_messages:
        message_send_handle(message)


def update_timestamp(partner:Partnership):
    ses = Session()
    target = ses.query(Partnership).filter_by(id=partner.id).first()
    target.last_check = datetime.datetime.now()
    ses.commit()
    ses.close()
    return target

if __name__ == '__main__':
    Session = sessionmaker(bind=db)
    session = Session()
    partners = session.query(Partnership).all()
    while True:
        for partner in partners:
            partner_loop(partner)
        break
