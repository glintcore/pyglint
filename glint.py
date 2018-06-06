import requests

class GlintError(Exception):
    pass

class Glint:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def add_file(self, name, data):
        try:
            self.post_file(name, data)
            new_file = GlintFile(self.username, name)
            return new_file
        except GlintError as ge:
            print("Unable to create new file: %s" % ge)

    def retrieve_file(self, name):
        try:
            glint_file = self.get_file(name)
            return glint_file
        except GlintError as ge:
            print("Unable to retrieve file: %s" % ge)

    def get_auth(self):
        auth = HTTPBasicAuth(self.username, self.password)
        return auth

    def post_file(name, data):
        auth = self.get_auth()
        url = "%s/%s" % (self.host, name)
        response = requests.post(url, data=string, auth=auth)
        if r.status_code != 201:
            raise GlintError("Unable to create data file: %s" % r.text



class GlintFile:
    def __init__(self, username, name):
        self.username = username
        self.name = name





