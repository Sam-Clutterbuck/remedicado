# Remedicado Sql Structure
## Remediation table
The remediation table stores the core remediation data for the program.

 - `remediation_id` - This is the id used by remedicado to track the progress of a remediation
 - `remediation_name` - This is the human readable name of the remediation, usually a brief summary of the vulnerability ***e.g. RHEL 7 - apache server vulnerability***
 - `remediation_desc` - This is the long form description of the vulnerability usually detailing what the vulnerability is, what it does / its impact and a solution to fix it
 - `remediation_sev` - This is the cvss v3 severity of the vulnerability used to highlight the level of risk and used by remedicado to determine status against policy lengths
 - `remediation_date_reported` - This is the first date that the vulnerability was reported
 - `remediation_last_updated` - This is the date the remediation was last updated for either new affected ips or to update remediated ips
 - `remediation_source`* - This is the id of the linked source used to determine the source of this remediation discovery 
 - `remediation_source_id`* - This is the numerical id of the vulnerability provided by selected source
 
 ***\* - Sources detailed in more depth below***

## Affected ips
The affected ips table links the remediations to the ips that are affected by their vulnerability via their respective ids

 - `remediation_id` - This is the id of the remediation from the remediation table
 - `ip_list_id` - This is the id of the ip that is affected
 - `date_reported` - This is the date that the ip was reported to be affected by the vulnerability. This is used to calculate policy status before remediation date so newly discovered affected ips aren't unfairly marked as out of policy when just discovered
 - `remediated` - This simply lists whether the ip has been remediated for this vulnerability. This can be overwritten manually, however there are checks that run on import that mark ips as remediated if they don't appear in later imports of a vulnerability source
 - `last_seen` - This shows the date of the last imported report that contained reference to this ip being affected by the corresponding vulnerability
 - `remediated_previously` - This details if this is a vulnerability that was previously remediated but happened to re-appear for whatever reason

## Ip list
This is simply a list of all ips associated with your network that have been passed through imported reports. ***Note that this may not be the full network as only ips top be remediated will have been imported.***

 - `ip_list_id` - This is the unique id of the ip
 - `ip_list_address` - This is the ip address of the system

## Source list
The source list contains a list of potential sources for imports. These sources are used as a key identifier for remediations. 

Reports imported to remedicado need to contain a source name and numeric id. The name is compared against this source list to see if it exists. Any unknown sources **will not** be imported to the system. 

The numeric Id is used to identify a remediation **not the remediation name**, therefore even if the sources match, if a already referenced source id is used that remediation will be overwritten even if the vulnerability is different. 
To overcome this the source id should be a unique id provided by your source of choice. For example: 

 - Nessus sources should use the plugin ID as the source id as these are unique so won't repeat and also act as a convenient point of reference
 - You could also use cve numbers (\<YEAR\>\<ID\> in a single integer due to needing a numerical integer) which again function as a useful point for extra research if required
 - Lastly if you have a contracted pen-test you they could have their discovered findings numerically referenced and that can be used as the id. Again this could be used as a reference point in the more detailed report

The Source list only contains 2 values
- `source_id` - This is the unique id of the source referenced in the remediation table
 - `source_name` - This is the human readable name of the source that should be found in the imported report
