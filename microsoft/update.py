import json
import urllib.request as request
from pprint import pprint
import os
from datetime import datetime

ENDPOINT_URL = "https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7"
IGNORE_URLS = [ 
	"*linkedin*" 
]

ALWAYS_WILDCARD = [
	"microsoft.cloud",
    "microsoft365.com",
    "msedge.net",
    "azure.net",
    "microsoft.com",
    "office.net",
    "azureedge.net",
    "azure.com",
    "microsoftonline-p.com",
    "msocdn.com",
    "windows.com",
    "microsoftonline.com",
    "outlook.com",
    "office.com",
    "office.net",
    "windows.net",
    "onenote.com",
    "onenote.net",
    "office365.com",
    "onedrive.com",
    "outlook.com",
    "trafficmanager.net", # Scheint eine CDN-Adresse von Microsoft zu sein (Dokumentation dieser URL unvollständig, siehe https://github.com/SchulIT/pihole-lists/issues/1)
    "microsoftpersonalcontent.com", # soll wohl auch zu Microsoft SharePoint gehören
    "fb-t-msedge.net", # Scheint eine CDN-Adresse für Azure zu sein (wird für Kursnotizbücher auf iOS benötigt)
    "spo-msedge.net", # Scheint eine CDN-Adresse für SharePoint zu sein (wird für Kursnotizbücher auf iOS benötigt)
]

wildcards = [ ]
domains = [ ]

def isWildcard(url):
	return url[0:1] == "."

def isIgnored(url):
	for ignoreURL in IGNORE_URLS:
		if url.find(ignoreURL) != -1:
			return True
	return False
'''
Lösche alles bis zum letzten *
Beispiele:
- example.com -> example.com
- *.example.com -> .example.com
- foo.*.example.com -> .example.com 
'''
def cleanUp(url):
    idx = url.rfind('*')
	
    if idx == -1:
        return url

    return url[(idx+1):]
	
'''
Testet, ob eine URL bereits Teil einer Subdomain ist.
'''
def isAlreadyPartOfSubdomain(url):
    for wildcard in wildcards:
        if url[-(len(wildcard)+1):] == ("." + wildcard):
            return True
		
    return False

for domain in ALWAYS_WILDCARD:
    wildcards.append(domain)

response = request.urlopen(ENDPOINT_URL)
json = json.loads(response.read())

for endpoint in json:
    if not 'urls' in endpoint:
        continue
    
    for url in endpoint['urls']:
        if isIgnored(url):
            continue
        
        url = cleanUp(url)

        if not isAlreadyPartOfSubdomain(url):
            if isWildcard(url):
                wildcards.append(url[1:])
            else:
                domains.append(url)


wildcards.sort()
domains.sort()

output_directory = os.path.dirname(os.path.realpath(__file__))
handle = open(output_directory + "/microsoft365-wildcard", "w")
handle.write("# Wildcard-Domains fuer Microsoft 365\n")
handle.write("# Generiert aus: " + ENDPOINT_URL + "\n")
handle.write("# Generiert am: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")

for wildcard in wildcards:
    handle.write("@@||" + wildcard + "^\n")

handle.close()

handle = open(output_directory + "/microsoft365-specific", "w")
handle.write("# Nicht-Wildcard-Domains fuer Microsoft 365\n")
handle.write("# Generiert aus: " + ENDPOINT_URL + "\n")
handle.write("# Generiert am: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")

for domain in domains:
    handle.write(domain + "\n")

handle.close()