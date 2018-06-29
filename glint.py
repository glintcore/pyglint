import csv
import requests
from requests.auth import HTTPBasicAuth

class GlintError(Exception):
    pass

class Glint:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def add_file_string(self, name, data):
        try:
            self.put_file(name, data)
            new_file = GlintFile(self.username, name, self)
            return new_file
        except GlintError as ge:
            print("Unable to create new file: %s" % ge)

    def add_file_path(self, name, path):
        try:
            with open(path, "r") as file_handle:
                content = file_handle.read()
                self.put_file(name, content)
                new_file = GlintFile(self.username, name, self)
                return new_file
        except GlintError as ge:
            print("Unable to create new file: %s" % ge)

    def get_file_list(self):
        url = "%s/%s" % (self.host, self.username)
        response = requests.get(url)
        if response.status_code != 200:
            raise GlintError("Got code %s trying to retrieve file listing: %s" %\
                    (response.status_code, response.text))
        csv_string = response.content.decode('utf-8')
        csv_lines = csv_string.splitlines()
        reader = csv.reader(csv_lines, delimiter=',')
        reader_list = list(reader)
        file_list = []
        reader_list = reader_list[1:] #skip heading
        for row in reader_list:
            file_list.append(row[0])
        return file_list

    def verify_file(self, name):
        """
        Throw a GlintError if the named file does not exist
        for this connection
        """
        file_list = self.get_file_list()
        if name not in file_list:
            raise GlintError("Could not find file %s for this user" % name)

    def get_glint_file(self, name):
        """
        Get a GlintFile for an existing file, by name
        """
        try:
            self.verify_file(name)
            glint_file = GlintFile(self.username, name, self)
            return glint_file
        except GlintError as ge:
            print("Unable to retrieve file: %s" % ge)

    def get_auth(self):
        auth = HTTPBasicAuth(self.username, self.password)
        return auth

    def put_file(self, name, data):
        auth = self.get_auth()
        url = "%s/%s/%s" % (self.host, self.username, name)
        data_json = { "data" : data }
        response = requests.put(url, json=data_json, auth=auth)
        if response.status_code != 201:
            raise GlintError("Unable to create data file. Got code %s: %s"\
                    % (response.status_code, response.text))
        return response

    def get_file_data(self, name, transform_query=None):
        auth = self.get_auth()
        if transform_query:
            url = "%s/%s/%s?%s" % (self.host, self.username, name, transform_query)
        else:
            url = "%s/%s/%s" % (self.host, self.username, name)
        response = requests.get(url, auth=auth)
        if response.status_code != 200:
            raise GlintError("Unable to retrieve file %s: %s" % (name, response.text))
        return response

    def put_metadata(self, name, attribute, element):
        auth = self.get_auth()
        url = "%s/%s/%s.%s" % (self.host, self.username, name, attribute)
        payload = { "metadata" : element }
        response = requests.put(url, json=payload, auth=auth)
        if response.status_code != 200:
            raise GlintError("Got error response %s when tagging dataset %s: %s" \
                    % (response.status_code, name, response.text))


class GlintFile:
    def __init__(self, username, name, connection):
        self.username = username
        self.name = name
        self.connection = connection

    def get_data(self, columns=None, data_format=None):
        transform_query = ""
        if columns:
            transform_query = "show(%s)" % ",".join(columns)
        if data_format:
            transform_query = "%sas(%s)" % (transform_query, data_format)

        return self.connection.get_file_data(self.name, transform_query).text

    def tag(self, attribute, metadata):
        self.connection.put_metadata(self.name, attribute, metadata)








