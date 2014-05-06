Usage :
python import_reports.py -a deployreporttemplates -o {organization_name} -u {apigee_userid} -p {apigee_password} -z {reports_location} -l {base_path}

Example :
python apigeeanalytics.py -a deployreporttemplates -o testorg -u testuser@apigee.com -p test1234 -z /Users/testuser/test.zip -l https://api.enterprise.apigee.com/v1

Documentation :

-a Action for Apigee analytics. (Supported actions are deployreporttemplates)
-o Apigee organization name
-u Apigee user name
-p Apigee password
-l Apigee API URL (optional, defaults to https://api.enterprise.apigee.com/v1)
-z ZIP file which contains the reports
-h Help
-f force update (incase a report with same name already exists)



