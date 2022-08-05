import importlib
import json
import logging
import os

import requests as requests

from quickbase_model_maker.utils import to_file_name, as_camel_case

fmt = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(fmt)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


class Table:
    def __init__(self, name, table_id, app_name, app_id):
        name = name.lower().replace(' ', '_')
        self.name = to_file_name(name)
        self.app_name = to_file_name(app_name)
        self.app_name_label = app_name
        self.app_id = app_id
        self.table_id = table_id
        self.fields = []

    def render(self, path: str):
        cls_name = self.name[:-1] if self.name[-1] == 's' else self.name
        cls_name = as_camel_case(cls_name)
        lines = [
            f'class {cls_name}:\n'
        ]

        # add fields
        for f in self.fields:
            lines.append(f'\t{f[1]} = {f[0]}\n')

        # add table_id method
        lines.append(f'\n\t@staticmethod\n\tdef table_id():\n\t\treturn "{self.table_id}"\n')

        # add app method
        lines.append(f'\n\t@staticmethod\n\tdef app():\n\t\treturn "{self.app_name_label}"\n')

        # add app_id method
        lines.append(f'\n\t@staticmethod\n\tdef app_id():\n\t\treturn "{self.app_id}"\n')

        # replace tabs with spaces
        lines = [line.replace('\t', '    ') for line in lines]

        # check if directory exists
        if not os.path.exists(f'{path}/{self.app_name}'):
            os.makedirs(f'{path}/{self.app_name}')

        # write to file
        f = open(f'{path}/{self.app_name}/{self.name}.py', 'w')
        f.writelines(lines)
        f.close()

        # check if init exists in directory, if not, create it
        if not os.path.exists(f'{path}/{self.app_name}/__init__.py'):
            f = open(f'{path}/{self.app_name}/__init__.py', 'w')
            f.close()

        logger.debug(f'Created model for ---> {self.name}')


class QuickbaseModelMaker:
    def __init__(self, realm: str, auth: str, **kwargs):
        """
        :param realm: The realm to connect to
        :param auth: The authentication token to use
        """
        self.realm = realm if '.' not in realm else realm.split('.')[0]
        self.auth = auth
        s = requests.Session()
        headers = {
            'QB-Realm-Hostname': f'{self.realm}.quickbase.com',
            'User-Agent': 'python/QuickbaseModelMaker',
            'Authorization': f'QB-USER-TOKEN {auth}'
        }
        s.headers = headers
        self.requests = s
        self.references_directory = kwargs.get('references_directory', './references')
        # registrations
        self.registered_tables = []
        self.tables = []

        # check if references directory exists
        if not os.path.exists(self.references_directory):
            os.makedirs(self.references_directory)
            # create __init__.py file in references directory
            f = open(f'{self.references_directory}/__init__.py', 'w')
            f.write('TABLES = {}')
            f.close()

    def sync(self, only_new_tables=False, **kwargs):
        """
        Syncs tables with Quickbase, creates models based off of the tables
        :param only_new_tables: Only create models for tables that have not previously been registered
        :param kwargs:
        :return:
        """

        created_tables = {}
        # try to import created tables
        try:
            references_import = importlib.import_module(f'references', package='references')
            created_tables = references_import.TABLES
        except ImportError:
            logger.info('No references found')
            # create __init__.py file
            f = open(f'{self.references_directory}/__init__.py', 'w')
            f.close()

        # handle migrate
        app_map = {}
        for table in self.registered_tables:

            # check if table is already created
            if table[1] in created_tables.keys() and only_new_tables:
                logger.info(f'Table "{table[1]}" already synced, skipping...')
            else:
                app_id = table[0]
                table_id = table[1]
                # if app_id not in app_map, create it
                if app_map.get(app_id) is None:
                    app_name_r = self.requests.get(f'https://api.quickbase.com/v1/apps/{app_id}')
                    if app_name_r.ok:
                        app_map.update({app_id: app_name_r.json()['name']})

                # get table data
                r = self.requests.get(f'https://api.quickbase.com/v1/tables/{table_id}?appId={app_id}')

                # if table data is ok, proceed to querying fields
                if r.ok:
                    table_data = r.json()
                    table_name = table_data['name']
                    r_fids = self.requests.get(f'https://api.quickbase.com/v1/fields?tableId={table_id}')

                    # if fields are ok, proceed to creating Table object
                    if r_fids.ok:
                        table_fields = []
                        for field in r_fids.json():
                            label_raw = field.get('label')
                            label_alpha = ''.join(c for c in label_raw if c.isalpha() or c.isspace() or c.isdigit())
                            label = label_alpha.upper().replace(' ', '_')
                            table_fields.append((field.get('id'), label))

                        # create table object, assign it fields
                        t = Table(table_name, table_id, app_name=app_map.get(app_id), app_id=app_id)
                        t.fields = table_fields
                        self.tables.append(t)
                        logger.debug(f'Synced table ---> {table_name}')
                else:
                    raise ConnectionError(f'Could get table {table_id}, error: {r.text}')
                created_tables.update(
                    {table_id: {'name': table_name, 'app_id': app_id, 'app_name': app_map.get(app_id)}})

        # write new created tables
        f = open(f'{self.references_directory}/__init__.py', 'w')
        f.write(f'TABLES = {json.dumps(created_tables, indent=4)}\n')
        f.close()

        # create references directory
        os.makedirs(self.references_directory, exist_ok=True)

        # register tables
        logger.info(f'Creating models from ({len(self.tables)}) tables')
        for table in self.tables:
            table.render(self.references_directory)

    def create_from_app_url(self, url: str):
        raise NotImplementedError()

    def register_tables(self, tables: list):
        """
        Creates models from tables, given a list of tuples of (app_id, table_id)
        :param tables: list of tuples of (app_id, table_id)
        """
        logger.info(f'Registering ({len(tables)}) tables')
        for table in tables:
            # will add more info to table object, eventually
            table_data = (table[0], table[1])
            self.registered_tables.append(table_data)
