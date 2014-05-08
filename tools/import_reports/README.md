Import Reports
===============
Usage :
------
python import_reports.py -a deployreporttemplates -o {organization_name} -u {apigee_userid} -p {apigee_password} -z {reports_location} -l {base_path}

Example :
python apigeeanalytics.py -a deployreporttemplates -o testorg -u testuser@apigee.com -p test1234 -z /Users/testuser/test.zip -l https://api.enterprise.apigee.com/v1

-a Action for Apigee analytics. (Supported actions are deployreporttemplates) <BR>
-o Apigee organization name <BR>
-u Apigee user name <BR>
-p Apigee password <BR>
-l Apigee API URL (optional, defaults to https://api.enterprise.apigee.com/v1) <BR>
-z ZIP file which contains the reports <BR>
-h Help <BR>
-f force update (incase a report with same name already exists)<BR>


