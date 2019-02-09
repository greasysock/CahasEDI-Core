import support.config as config
from support.edi import stream_handle
import support.storage.connection as connection
from support.storage.connection import Partnership, Message, Status, Acknowledge
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
    def ack_process_handle(message: stream_handle.EdiFile):
        session = Session()

        ack_message = Acknowledge()
        ack_message.interchange_control_number = int(message.edi_header.ISA[13])
        ack_message.ack_content = message.edi_header.ack.edi_header.get_all_bytes_lists()
        ack_message.partner_id = partner.id
        ack_message.status = Status.send
        session.add(ack_message)
        session.commit()
        session.close()

    def receive_message_handle(content: generic.Template):
        session = Session()

        tmp_message = Message()

        if content.GS:
            group_number = int(content.GS[6])
            tmp_message.group_control_number = group_number
        set_number = int(content.ST[2])

        tmp_message.date = datetime.datetime.now()
        tmp_message.content = content.get_bytes_list()
        tmp_message.partner_id = partner.id
        tmp_message.interchange_control_number = int(content.ISA[13])
        tmp_message.transaction_control_number = set_number

        tmp_message.template_type = content.template_type
        tmp_message.status = Status.received
        session.add(tmp_message)
        session.commit()
        session.close()

    # TODO
    def receive_ack_handle(content: x12_997):
        pass

    # Receiving end for incoming messages
    def receive_handle(message: stream_handle.EdiFile):
        contents = message.edi_header.get_all_content()
        if message.edi_header.ack:
            ack_process_handle(message)

        for content in contents:
            if content.template_type == x12_997.description.identifier_code:
                receive_ack_handle(content)
            else:
                receive_message_handle(content)

    # TODO
    def message_send_handle(message: Message):
        pass

    def ack_send_handle(ack: Acknowledge):
        print(ack.ack_content)

        ediheader = stream_handle.EdiHeader(ack.ack_content)

        print(ediheader)
        print(ack.ack_content)
        pass

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
    session.close()
    while True:
        for partner in partners:
            partner_loop(partner)
        break
