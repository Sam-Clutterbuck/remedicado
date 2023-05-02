#from src import Cli

from re import search

for i in ip:
    x = search(r"(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}", i)
    print (x)

quit()

Cli.Cli_Start()

#'data/files/Tenable_Remediations_Breakdown.csv','test_data/DEMO_TOP_10.csv'