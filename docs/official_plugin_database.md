# Official Plugin Database
> The following plugins have been officially accepted into the plugin infrastructure for Remedicado. These plugins are confirmed to be working to the best of our knowledge and are deemed suitable for use.

# Plugins

## CSV comparison
### Details
**Created by:** @Sam-Clutterbuck

**Last Updated:** 27/04/2023

**Version:** 0.0.1 

 **Hash:** *FECF19E3E5E3FE6160565075EC4C7013C9D7088E5180DCF5938F06A555E0C4A8*

### Description
This plugin takes a source breakdown csv provided by remedicado, containing a list of all source ids and their remediation stats; and compares it with a top xxxx csv from your selected source, containing a list of vulnerabilities found by source ID. The outcome of the comparison is a merged csv containing all of the provided source vulnerabilities and whether they have been reported or not and if so, lists how many ips have been reported numerically. Once produced the csv can be opened in any excel sheet viewing program to be used to determine what vulnerabilities to focus on.

The Top xxxx csv needs to be configured in a certain way in order to merge properly with the source breakdown and create a suitable remediation -> vulnerability summary. This configuration should be under the **exact** following csv headers.
```
'remediation_name','source_id','severity','affected_ip_count'
```

### Example usage
Here is a simple example showing a user comparing the Tenable source breakdown to a top_10.csv they extracted from tenable.

***The following commands are run via the Remedicado Cli***

```
Enter a command to run: rp
Would you like to view installed plugins?
[y]es or [n]o?
y

Installed Plugins
csv_comparison | [0]

Select a plugin number to view options:
0

List plugins for csv_comparison: 

[0] | command : init
 Arguments: {'breakdown file location': <class 'str'>, 'Top Vuln file location': <class 'str'>}

Would you like to run a plugin command?
[y]es or [n]o?
y

Select a plugin command number:
0

Enter breakdown file location:
data/files/Tenable_Remediations_Breakdown.csv

Enter Top Vuln file location:
test_data/DEMO_TOP_10.csv

<Print copy of table>
Created file : data/files/Vulnerability_List_2023_04_27.csv
```