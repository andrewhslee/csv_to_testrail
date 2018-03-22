import csv
import sys
import json
import requests

from testrail import *

client = APIClient("https://wishabi.testrail.com")
client.user = "andrew.lee@wishabi.com"
client.password = "Dlgkstp9."

PROJECT_ID = 76
SUITE_COL = 'Ticket ID'
SECTION_COL = 'Section'
CASE_COL = 'Case'
INSTR_COL = ''
EXPECTED_COL = 'Expected'

#Get Command Line Arguments
def main(argv):
    input_file = ''
    if sys.argv[1]:
        input_file = sys.argv[1]
    else:
        print "Error: Must enter a file name"
        sys.exit(1)
    readFile = read_csv(input_file)
    suites = client.send_get('get_suites/' + str(PROJECT_ID))
    suite_names_id = {}
    for s in suites:
        suite_names_id[s['name'].strip()] = s['id']
    json_format = json.loads(readFile)
    i = ''
    print readFile
    print "This is how your csv turned into json."
    # try:
    #     i = input ("Enter to continue")
    # except SyntaxError:
    #     i = None
    # if input == None:
    #     print "here"
    currSection = ''
    currSuite = ''
    suite_id = 0
    section_id = 0
    for test in json_format:
        if test[SUITE_COL] != '':
            currSuite = test[SUITE_COL]
        
        if currSuite in suite_names_id:
            print suite_names_id
            suite_id = suite_names_id[currSuite]
            if test[SECTION_COL] != '':
                currSection = test[SECTION_COL]
                if get_section_id(currSection, suite_id) == None:
                    section_id = create_section(currSection, suite_id)
                else:
                    section_id = get_section_id(currSection, suite_id)
        else:
            suite_id = create_suite(currSuite)
            currSection = test[SECTION_COL]
            section_id = create_section(currSection, suite_id)

        add_to_section(section_id, suite_id, test[CASE_COL], test[EXPECTED_COL])
           
            
#Read CSV File
def read_csv(file):
    with open(file) as csvfile:
        # enter the field names you used for the CSV file
        reader = csv.DictReader(csvfile)
        out = json.dumps( [ row for row in reader ], sort_keys=False, indent=4, separators=(', ', ': '),encoding="utf-8",ensure_ascii=False)  
        return out

def create_suite(suite_name):
    data = {
        'name' : suite_name
    }
    resp = client.send_post('add_suite/' + str(PROJECT_ID), data)
    return resp['id']

def create_section(section_name, suite_id):
    data = {
        'suite_id' : suite_id,
        'name' : section_name, 
    }
    resp = client.send_post('add_section/76', data)
    return resp['id']
    

def add_to_section(section_id, suite_id, case_name, case_expected = None, case_instructions = None):
    cases = client.send_get('get_cases/' + str(PROJECT_ID) + '&suite_id=' + str(suite_id) + '&section_id=' + str(section_id))
    case_names = []
    for c in cases:
        case_names.append(c['title'])
    
    data = {
        'title' : case_name,
        'custom_steps' : case_instructions,
        'custom_expected' : case_expected,
    }
    if case_name.strip() in case_names:
        if c['custom_steps'] == case_instructions and c['custom_expected'] == case_expected:
                return
        elif c['custom_steps'] != case_instructions or c['custom_expected'] != case_expected:
            client.send_post('update_case/' + str(c['id']), data)
    else:
        client.send_post('add_case/' + str(section_id), data)

def get_section_id(section_name, suite_id):
    sections = client.send_get('get_sections/' + str(PROJECT_ID) + '&suite_id=' + str(suite_id))
    for s in sections:
        if s['name'] == section_name:
            return s['id']

if __name__ == "__main__":
   main(sys.argv[1:])
