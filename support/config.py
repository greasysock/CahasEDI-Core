import json, os, sys
# Each partnership starts in config file, then moves to database where it is given a unique id


class Partner:
    def __init__(self, id_qualifier, id, watch_dir, send_dir):
        self._id = id
        self._id_qualifier = id_qualifier
        self._watch_dir = watch_dir
        self._send_dir = send_dir

    @property
    def id(self):
        return self._id

    @property
    def id_qualifier(self):
        return self._id_qualifier

    @property
    def watch_dir(self):
        return self._watch_dir
    @property
    def send_dir(self):
        return self._send_dir


class File:

    def __init__(self, config_file : str):
        self._partnership_definition = {
            'ID Qualifier': 'ZZ',
            'Interchange ID': 'SomeID',
            'Watch Directory': './SomeWatchDirectory',
            'Send Directory': './SomeSendDirectory'
        }

        self._database_definition = {
            'type':'postgresql',
            'login': 'login',
            'password': 'pass',
            'database name' : 'cahasEDI'
        }

        self._partnerships = list()
        self._id_qualifier = "ZZ"
        self._id = "SomeID"
        self._db_login = None
        self._db_pass = None
        self._db_name = None

        try:
            nothing = False
            with open(config_file, "r") as file:
                if file.readlines() == []:
                    nothing = True
            if nothing:
                self._setup_conf(config_file)
            self._parse_conf(config_file)
        except FileNotFoundError:
            self._setup_conf(config_file)

    def _setup_conf(self, file_name : str):

        structure = {
            "ID Qualifier" : self._id_qualifier,
            "ID" : self._id,
            "Partnerships" : [self._partnership_definition],
            "db" : self._database_definition,
        }
        out = json.dumps(structure, indent=2, sort_keys=True)
        with open(file_name, "w") as file:
            file.write(out)
        print("Configuration file created. Please configure.")
        sys.exit(0)

    def _parse_conf(self, file_name : str):

        content = None
        with open(file_name, "r") as file:
            content = json.loads(file.read())

        self._id = content['ID']
        self._id_qualifier = content['ID Qualifier']
        self._db_login = content['db']['login']
        self._db_pass = content['db']['password']
        self._db_name = content['db']['database name']

        for partner in content['Partnerships']:
            p = Partner(partner['ID Qualifier'],
                        partner['Interchange ID'],
                        partner['Watch Directory'],
                        partner['Send Directory'])
            self._partnerships.append(p)

    @property
    def id(self):
        return self._id
    @property
    def id_qualifier(self):
        return self._id_qualifier
    @property
    def db_login(self):
        return self._db_login
    @property
    def db_password(self):
        return self._db_pass
    @property
    def db_name(self):
        return self._db_name
    def get_partners(self):
        return self._partnerships
