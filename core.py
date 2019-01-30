import support.config as config
import support.storage.connection as connection
config_file = "config.json"

conf = config.File(config_file)
db = connection.connect(conf.db_login,conf.db_password, conf.db_name, "postgresql")

