
from __future__ import print_function
import sys
import httplib2
import os
import io

from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)

    return credentials

def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    # ===========

    results = service.files().list(
        q="name = 'TextEncounterRegister'", fields="files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print("TextEncounterRegister.docx not found")
    else:
        item = items[0]
        request = service.files().export_media(
            fileId=item['id'],
            mimeType='text/plain')
        fh = io.FileIO('register.txt', mode='wb')
        downloader = MediaIoBaseDownload(fh, request, chunksize=1024*1024)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print ("Download %d%%." % int(status.progress() * 100))

        with open('register.txt', 'r') as file:
            print(file.read())

    # ===================================

    results = service.files().list(
        pageSize=10,q="name = 'TE Format plain text with tags'",fields="files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))

            request = service.files().export_media(fileId=item['id'],
                                                         mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

            fh = io.FileIO('{}.docx'.format(item['name']), mode='wb')
            downloader = MediaIoBaseDownload(fh, request, chunksize=1024*1024)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print ("Download %d%%." % int(status.progress() * 100))

    

if __name__ == '__main__':
    print(sys.version)
    main()