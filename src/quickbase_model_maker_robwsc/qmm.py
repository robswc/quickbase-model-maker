import os

import requests as requests


def ensure_dirs(path):
    pass


class Table:
    def __init__(self, name, table_id):
        self.name = name.lower()
        self.table_id = table_id
        self.fields = []

    def render(self, path: str):
        cls_name = self.name[:-1] if self.name[-1] == 's' else self.name
        cls_name = cls_name.capitalize()
        lines = [
            f'class {cls_name}:\n'
        ]

        # add fields
        for f in self.fields:
            lines.append(f'\t{f[1]} = {f[0]}\n')

        # add get_table_id method
        lines.append(f'\n\t@staticmethod\n\tdef get_table_id():\n\t\treturn "{self.table_id}"\n')

        # replace tabs with spaces
        lines = [line.replace('\t', '    ') for line in lines]

        f = open(f'{path}/{self.name}.py', 'w')
        f.writelines(lines)
        f.close()


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
        self.tables = []

    def sync(self):

        # create references directory
        os.makedirs(self.references_directory, exist_ok=True)

        for table in self.tables:
            table.render(self.references_directory)

    def create_from_app_url(self, url: str):
        raise NotImplementedError()

    def register_tables(self, tables: list):
        """
        Creates models from tables, given a list of tuples of (app_id, table_id)
        :param tables: list of tuples of (app_id, table_id)
        """
        for table in tables:
            app_id = table[0]
            table_id = table[1]
            r = self.requests.get(f'https://api.quickbase.com/v1/tables/{table_id}?appId={app_id}')
            if r.ok:
                table_data = r.json()
                table_name = table_data['name']
                r_fids = self.requests.get(f'https://api.quickbase.com/v1/fields?tableId={table_id}')
                if r_fids.ok:
                    table_fields = []
                    for field in r_fids.json():
                        label_raw = field.get('label')
                        label_alpha = ''.join(c for c in label_raw if c.isalpha() or c.isspace() or c.isdigit())
                        label = label_alpha.upper().replace(' ', '_')
                        table_fields.append((field.get('id'), label))

                    t = Table(table_name, table_id)
                    t.fields = table_fields
                    self.tables.append(t)
            else:
                raise ConnectionError(f'Could get table {table_id}, error: {r.text}')
