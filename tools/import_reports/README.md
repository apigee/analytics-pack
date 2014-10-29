Import Reports
===============
Usage :
------
python import_reports.py -o {organization_name} -u {apigee_userid} -p {apigee_password} -z {reports_location} -l {base_edge_path} 
<BR>
**Example** :
<BR>
python import_reports.py -o testorg -u testuser@apigee.com -p test1234 -z /Users/testuser/test.zip -l https://api.enterprise.apigee.com/v1

-o Apigee organization name <BR>
-u Apigee user name <BR>
-p Apigee password <BR>
-l Apigee API URL (optional, defaults to https://api.enterprise.apigee.com/v1) <BR>
-z ZIP file which contains the reports <BR>
-h Help <BR>
-f force update (incase a report with same name already exists)<BR>


