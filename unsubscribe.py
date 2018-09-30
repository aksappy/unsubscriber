
# coding: utf-8

# # Unsubscribe from your emails
# 
# This program will read your emails and collect all the links for unsubscription
# The collection of links is written to a file
# Then from the file the links are read, unique links are opened in the browser
# However, you will have to manually click on majority of the unsubscriptions.. sigh!
# 

# In[17]:


# Install google api client for python
# pip install --upgrade google-api-python-client
get_ipython().system('ls')


# In[5]:


#Imports
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64 # base64 lib
import re # regex lib

import webbrowser
import time
from urllib.parse import urlparse


# In[6]:


# URL REGEX for finding all types of links.
URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)()))"""

# If modifying these scopes, reimport the token.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'


# In[7]:


def filewriter(url):
    """ A simple file writer """
    f = open("links.csv", "a")
    f.write("%s\n" %url)
    f.close()


# In[8]:


def getemails(service, _pageToken):
    """Recursive function to read all the emails. 
    The google responses has next page token, 
    which is used to call the next page of emails"""
    msgs = service.users().messages().list(
        userId='me', pageToken=_pageToken).execute()
    if 'nextPageToken' in msgs:
        nextPageToken = msgs['nextPageToken']
    else:
        return True
    for msg in msgs['messages']:
        _id = msg['id']
        emailbody(service, _id)
    print("Next Page Token = %s" % nextPageToken)
    getemails(service, nextPageToken)


# In[9]:


def openlinks():
    f=open('links.csv','r')
    lines=f.readlines()
    lst = {}
    for line in lines:
        bln=line.startswith('http://') or line.startswith('https://')
        if bln is False:
            line='http://'+line
        parsed_uri = urlparse(line)
        result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        lst[result]=line
    for link in lst:
        webbrowser.open_new_tab(lst[link])


# In[10]:


def emailbody(service, _id):
    msg = service.users().messages().get(userId='me', id=_id).execute()
    payld = msg['payload']
    if 'parts' in payld:
        mssg_parts = payld['parts']  # fetching the message parts
        part_one = mssg_parts[0]  # fetching first element of the part
        part_body = part_one['body']  # fetching body of the message
        if 'data' in part_body:
            part_data = part_body['data']  # fetching data from the body
            # decoding from Base64 to UTF-8
            clean_one = part_data.replace("-", "+")
            # decoding from Base64 to UTF-8
            clean_one = clean_one.replace("_", "/")
            # decoding from Base64 to UTF-8
            clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))
            values = re.findall(URL_REGEX, str(clean_two))
            for val in values:
                if 'unsubscribe'  in val[0]:
                    filewriter(val[0])


# In[11]:


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    msg = service.users().messages().list(userId='me', q="unsubscribe").execute()
    output=getemails(service, msg['nextPageToken'])
    if output is True:
        openlinks()


# In[15]:


main()

