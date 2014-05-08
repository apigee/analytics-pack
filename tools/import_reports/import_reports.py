import getopt
import urllib2
import re
import sys
import json
from zipfile import ZipFile

provisioned_reports_for_org = None
is_already_fetched_reports_for_org = False


def run():
    apigee_url = 'https://api.enterprise.apigee.com/v1'
    username = None
    password = None
    organization = None
    input_file = None
    force_update = False
    options = 'o:u:p:b:l:z:h:f'

    opts = getopt.getopt(sys.argv[1:], options)[0]

    for o in opts:
        if o[0] == '-o':
            organization = o[1]
        elif o[0] == '-u':
            username = o[1]
        elif o[0] == '-p':
            password = o[1]
        elif o[0] == '-l':
            apigee_url = o[1]
        elif o[0] == '-z':
            input_file = o[1]
        elif o[0] == '-f':
            force_update = True
        elif o[0] == '-h':
            print_usage()
            sys.exit(0)

    badusage = False
    if username is None:
        badusage = True
        print '-u is required'
    if password is None:
        badusage = True
        print '-p is required'
    if organization is None:
        badusage = True
        print '-o is required'
    if input_file is None:
        badusage = True
        print '-z is required'

    if badusage:
        print_usage()
        sys.exit(1)

    if input_file.endswith('.json'):
        try:
            file_content = open(input_file, 'r').read()
            return handle_single_file(file_content, organization, username, password, apigee_url, force_update)
        except Exception, e:
            print 'unable to read the input file '+input_file
            print e
    elif input_file.endswith('.zip'):
        try:
            input_zip = ZipFile(input_file)
        except Exception, e:
            print 'unable to read the input file ' + input_file
            print e
            sys.exit(1)
        for file_name in input_zip.namelist():
            try:
                print 'processing file ' + file_name + '...'
                file_content = input_zip.read(file_name)
                return handle_single_file(file_content, organization, username, password, apigee_url, force_update)
            except Exception, e:
                print e
                print 'provisioning file ' + file_name + ' failed'
    else:
        print 'Invalid option for -z. Supported formats for Input File are zip and json'


def handle_single_file(file_content, organization, username, password, apigee_url, force_update):
    report_name = get_report_name(json.JSONDecoder().decode(file_content))
    if report_name is None:
        print 'unable to retrieve the report name from the file. add report name in the tags section'
        return None
    elif not already_provisioned(report_name, organization, username, password, apigee_url):
        provision_report_template(report_name, file_content, organization, username, password, apigee_url)
    else:
        print 'report ' + report_name + ' already provisioned'
        if force_update:
            print 'creating new report ' + report_name
            provision_report_template(report_name, file_content, organization, username, password, apigee_url)
            delete_old_report(report_name, organization, username, password, apigee_url)


def already_provisioned(report_name, organization, username, password, apigee_url):
    global provisioned_reports_for_org
    global is_already_fetched_reports_for_org
    if not is_already_fetched_reports_for_org:
        provisioned_reports_for_org = get_report_definitions_for_org(organization, username, password, apigee_url)

    if provisioned_reports_for_org is not None:
        return check_if_report_name_matches(report_name, provisioned_reports_for_org)
    return False


def delete_old_report(report_name, organization, username, password, apigee_url):
    print 'deleting old report '+report_name
    global provisioned_reports_for_org
    global is_already_fetched_reports_for_org
    if not is_already_fetched_reports_for_org:
        provisioned_reports_for_org = get_report_definitions_for_org(organization, username, password, apigee_url)

    if provisioned_reports_for_org is not None:
        report_uuid = get_uuid_of_report(report_name, provisioned_reports_for_org)
        if report_uuid is not None:
            try:
                url = apigee_url + "/organizations/" + organization + "/reports/"+report_uuid
                url = url.encode('utf-8')
                req = urllib2.Request(url, headers={'Authorization': basic_authorization(username, password)})

                req.get_method = lambda: 'DELETE'
                f = urllib2.urlopen(req)
                response = f.read()
                code = f.getcode()
                # print code
                f.close()
                print 'report ' + report_name + ' deleted successfully..'
            except Exception, e:
                print 'error while deleting report ' + report_name + ' .error is '+e
        else:
            print 'report uuid is not available. cannot delete old report'


# gets the reports definitions for an org
def get_report_definitions_for_org(org, username, password, apigee_url):
    global provisioned_reports_for_org
    global is_already_fetched_reports_for_org
    try:
        url = apigee_url+"/organizations/" + org + "/reports?expand=true"
        get_reports_request = urllib2.Request(url, headers={"Authorization": basic_authorization(username, password)})
        api_response = urllib2.urlopen(get_reports_request).read()
        provisioned_reports_for_org = json.JSONDecoder().decode(api_response)
        is_already_fetched_reports_for_org = True
    except Exception, e:
        print e
        return None

    return provisioned_reports_for_org


def provision_report_template(report_name, report, organization, username, password, apigee_url):
    try:
        # data = json.dumps(report)
        clen = len(report)
        url = apigee_url+"/organizations/" + organization + "/reports"
        req = urllib2.Request(url, report, {'Content-Type': 'application/json', 'Content-Length': clen,
                                                     'Authorization': basic_authorization(username, password)})
        f = urllib2.urlopen(req)
        response = f.read()
        code = f.getcode()
        #print code
        f.close()
        print 'report '+report_name+' provisioned successfully..'
    except Exception, e:
        print e

def get_uuid_of_report(report_name, list_of_reports):
    if list_of_reports is not None:
        for item, itemVal in list_of_reports.iteritems():
            if item == "qualifier":
                for eitem in itemVal:
                    if eitem.has_key("name"):
                        try:
                            tags = eitem["tags"]
                            if report_name == tags[0]:
                                report_uuid = eitem["name"]
                                return report_uuid
                        except:
                            print "found older format. skipping.."
    return None


def check_if_report_name_matches(report_name, list_of_reports):
    if list_of_reports is not None:
        for item, itemVal in list_of_reports.iteritems():
            if item == "qualifier":
                for eitem in itemVal:
                    if eitem.has_key("tags"):
                        try:
                            tags = eitem["tags"]
                            if report_name == tags[0]:
                                return True
                        except:
                            print "found older format"
    return False


def get_report_name(content):
    if content is not None:
        for item, itemVal in content.iteritems():
            if item == "tags":
                try:
                    report_name = itemVal[0]
                    #print report_name
                    return report_name
                except:
                    print "found older format. hence ignoring"
                    return None
    return None


# Return TRUE if any component of the file path contains a directory name that
# starts with a "." like '.svn', but not '.' or '..'
def path_contains_dot(p):
    c = re.compile('\.\w+')
    for pc in p.split('/'):
        if c.match(pc) is not None:
            return True
    return False


def print_usage():
    print 'Usage: apigeeanalytics -o [organization]'
    print '         -u [username] -p [password]'
    print '         -l [apigee API url] -z [zip file] -h'
    print ''
    print '-o Apigee organization name'
    print '-u Apigee user name'
    print '-p Apigee password'
    print '-l Apigee API URL (optional, defaults to https://api.enterprise.apigee.com/v1)'
    print '-z zip/json file to save'
    print '-f flag to force update a report (In case a report with same name already exists.)'
    print '-h Print this message'


def basic_authorization(user, password):
    s = user + ":" + password
    return "Basic " + s.encode("base64").rstrip()


def main():
    run()

if __name__ == '__main__':
    main()
