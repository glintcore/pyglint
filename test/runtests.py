import sys
import os
package_root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, package_root_path)
import unittest
from pyglint import glint
import argparse
import uuid

#Tests
class GlintTest(unittest.TestCase):
    
    def setUp(self):
        self.host = os.environ.get('GLINTHOST')
        self.user = os.environ.get('GLINTUSER')
        self.passw = os.environ.get('GLINTPASS')
        test_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.join(test_dir, "resources")
        shark_file = os.path.join(resources_dir, "shark.csv")
        if not os.path.exists(shark_file):
            self.fail("Could not find test CSV file at path %s" % shark_file)
        self.shark_file_path = shark_file
        self.connection = glint.GlintConnection(self.host, self.user, self.passw)
        self.shark_file_name = uuid.uuid1().hex #random UUID prefix
        self.shark_glint_file = self.connection.add_file_path(self.shark_file_name,\
                self.shark_file_path)
    
    def tearDown(self):
        self.shark_glint_file.delete()

    def test_check_file_exists(self):
        self.connection.verify_file(self.shark_file_name)

    def test_get_nonexistant_file(self):
        message = ""
        try:
            self.connection.verify_file("foo-file-fake")
        except glint.GlintError as ge:
            message = ge.args[0]
        if not message.startswith("Could not find file"):
            raise Exception("Bad message: '%s'" % message)

    def test_retrieve_file(self):
        data = self.shark_glint_file.get_data()
        data_lines = data.split("\n")
        header_row = data_lines[0].split(",")
        self.assertTrue(header_row[0] == 'Shark_Number')
        self.assertTrue('Location_Code' in header_row)
        self.assertTrue('item_length' in header_row)
        self.assertTrue(header_row[-1] == 'Comments')

    def test_tag_file_metadata(self):
        self.shark_glint_file.tag('Shark_Number', 'dc:identifier')
        self.shark_glint_file.tag('Gear_Description', 'dc:description')
        data = self.shark_glint_file.get_data(with_metadata=True)
        header_row = data.split("\n")[0].split(',')
        self.assertTrue(header_row[0].endswith('{dc:identifier}'))
        self.assertTrue(header_row[2].endswith('{dc:description}'))

    def test_retrieve_file_subset(self):
        columns = [ 'Location_Code', 'item_length', 'Comments' ]
        data = self.shark_glint_file.get_data(columns=columns)
        header_row = data.split('\n')[0].split(',')
        self.assertTrue(len(header_row) == 3)

    def test_retrieve_file_tsv(self):
        data = self.shark_glint_file.get_data(data_format='tsv')
        data_lines = data.split("\n")
        header_row = data_lines[0].split("\t")
        self.assertTrue(header_row[0] == 'Shark_Number')
        self.assertTrue('Location_Code' in header_row)
        self.assertTrue('item_length' in header_row)
        self.assertTrue(header_row[-1] == 'Comments')

if __name__ == "__main__":
    #parser = argparse.ArgumentParser()
    #parser.add_argument("host", help="The hostname of our running Glint server")
    ##parser.add_argument("user", help="The Glint user to use for testing")
    #parser.add_argument("passw", help="The password for our Glint user")
    #args = parser.parse_args()
    #os.environ['GLINTHOST'] = args.host
    #os.environ['GLINTUSER'] = args.user
    #os.environ['GLINTPASS'] = args.passw
    unittest.main()

