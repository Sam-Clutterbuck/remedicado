# Remedicado Sql Structure

In order to store the remediation data for Remedicado you will need to install a mySQL server either locally or externally depending on your network configuration and requirements. This sql structure will need to contain the following tables.

To do so here is some SQL code to create the tables:

```
CREATE TABLE `sources` (
  `source_id` int NOT NULL AUTO_INCREMENT,
  `source_name` varchar(60) NOT NULL,
  PRIMARY KEY (`source_id`),
  UNIQUE KEY `source_id_UNIQUE` (`source_id`)
);
```

```
CREATE TABLE `ip_list` (
  `ip_list_id` int NOT NULL AUTO_INCREMENT,
  `ip_list_address` varchar(16) NOT NULL,
  PRIMARY KEY (`ip_list_id`),
  UNIQUE KEY `idip_list_ID_UNIQUE` (`ip_list_id`)
);
```

```
CREATE TABLE `remediation` (
  `remediation_id` int NOT NULL AUTO_INCREMENT,
  `remediation_name` varchar(100) NOT NULL,
  `remediation_desc` longtext NOT NULL,
  `remediation_sev` FLOAT NOT NULL,
  `remediation_date_reported` date NOT NULL,
  `remediation_last_updated` date DEFAULT NULL,
  `remediation_source` int NOT NULL,
  `remediation_source_id` int NOT NULL,
  PRIMARY KEY (`remediation_id`),
  UNIQUE KEY `remediation_id_UNIQUE` (`remediation_id`),
  KEY `source_id_idx` (`remediation_source`),
  CONSTRAINT `source_id` FOREIGN KEY (`remediation_source`) REFERENCES `sources` (`source_id`)
);
```

```
CREATE TABLE `affected_ips` (
  `remediation_id` int NOT NULL,
  `ip_list_id` int NOT NULL,
  `date_reported` date NOT NULL,
  `remediated` BOOL NOT NULL DEFAULT '0',
  `last_seen` date DEFAULT NULL,
  `remediated_previously` BOOL NOT NULL DEFAULT '0',
  KEY `remediation_ id_idx` (`remediation_id`),
  KEY `ip_list_id_idx` (`ip_list_id`),
  CONSTRAINT `ip_list_id` FOREIGN KEY (`ip_list_id`) REFERENCES `ip_list` (`ip_list_id`),
  CONSTRAINT `remediation_ id` FOREIGN KEY (`remediation_id`) REFERENCES `remediation` (`remediation_id`)
) ;
```

```
CREATE TABLE `uploaded_reports` (
  `uploaded_reports_id` int NOT NULL AUTO_INCREMENT,
  `remediation_id` int NOT NULL,
  `uploaded_reports_filename` varchar(100) NOT NULL,
  `uploaded_reports_upload_date` date NOT NULL,
  `uploaded_reports_hash` varchar(256) NOT NULL,
  PRIMARY KEY (`uploaded_reports_id`),
  KEY `remediation_id_idx` (`remediation_id`),
  CONSTRAINT `remediation_id` FOREIGN KEY (`remediation_id`) REFERENCES `remediation` (`remediation_id`)
);
```

```
CREATE TABLE `accounts` (
  `account_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `salt` varchar(128) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`account_id`)
  
);
```

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

### Accounts
The Accounts table is purely for storing the user accounts used to access the system

The accounts table contains 3 values
- `username` - the username for the user
- `salt` - the salt to be added to user password
- `password` - the hashed and salted password

