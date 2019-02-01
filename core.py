import support.config as config
from support.edi import stream_handle
import support.storage.connection as connection
from support.storage.connection import Partnership, Message, Status
from sqlalchemy.orm import sessionmaker
import os, datetime, io

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
            if partner.last_check is None:
                partner = update_timestamp(partner)
            edi_objs = check_watch_dir(partner.watch_dir, partner.last_check)
            if edi_objs != []:
                update_timestamp(partner)
                session = Session()
                for edi_obj in edi_objs:
                    contents = edi_obj.edi_header.get_all_content()
                    for content in contents:
                        tmp_message = Message()
                        tmp_message.date = datetime.datetime.now()
                        tmp_message.content = content.get_detailed_content()
                        tmp_message.partner_id = partner.id
                        tmp_message.template_type = content.template_type
                        tmp_message.status = Status.received
                        session.add(tmp_message)
                        session.commit()

        break
