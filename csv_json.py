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
    read = read_csv(input_file)
    suites = client.send_get('get_suites/' + str(PROJECT_ID))
    suite_names_id = {}
    for s in suites:
        suite_names_id[s['name'].strip()] = s['id']
    json_format = json.loads(read)
    i = ''
    print read
    print "This is how your csv turned into json."
    # try:
    #     i = input ("Enter to continue")
    # except SyntaxError:
    #     i = None
    # if input == None:
    #     print "here"
    for test in json_format:
        if test[SUITE_COL] != '':
            if test[SUITE_COL] not in suite_names_id:
                id = create_suite(test[SUITE_COL])
                suite_names_id[test[SUITE_COL]] = id
            
            suite_id = suite_names_id[test[SUITE_COL]]
            sections = client.send_get('get_sections/' + str(PROJECT_ID) + '&suite_id=' + str(suite_id))
            section_names_id = {}
            for s in sections:
                if s['name'] not in section_names_id:
                    section_names_id[s['name']] = s['id']
                else:
                    pass
            if test[SECTION_COL] == "":
                create_section("Cases", suite_id)
                section_id = section_names_id[test[SECTION_COL]]
                add_to_section(None, suite_id, test[CASE_COL], test[EXPECTED_COL])
            else:
                if test[SECTION_COL].strip() not in section_names_id:
                    create_section(test[SECTION_COL], suite_id)
                    section_id = section_names_id[test[SECTION_COL]]
                    add_to_section(section_id, suite_id, test[CASE_COL], test[EXPECTED_COL])
                else:
                    section_id = section_names_id[test[SECTION_COL]]
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
    client.send_post('add_section/76', data)
    

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

def get_suide_id(suite_name):
     suites = client.send_get('get_suites/'+ str(PROJECT_ID))
     for s in suites:
         if s['name'] == suite_name:
             return s['id']

def get_section_id(section_name, suite_id):
    sections = client.send_get('get_sections/' + str(PROJECT_ID) + '&suite_id=' + str(suite_id))
    for s in sections:
        if s['name'] == section_name:
            return s['id']

if __name__ == "__main__":
   main(sys.argv[1:])
