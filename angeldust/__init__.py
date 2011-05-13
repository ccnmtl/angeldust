#!ve/bin/python

import cStringIO
import plistlib
from pprint import pprint
from restclient import POST,GET
import os.path
import sys
import os
import urllib2
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from poster.encode import MultipartParam

import base64

class PCP:
    def __init__(self,base_url,username,password):
        self.BASE = base_url
        self.credentials = (username,password)
        self.session = None
        register_openers()
        
    def get_session(self):
        if not self.session:
            # need to login
            resp,contents = POST(self.BASE + "capture/login",
                                 params = {
                    'authenticating_user' : self.credentials[0],
                    'commit' : 'Log In',
                    'password' : self.credentials[1],
                    },
                                 # it ignores the login if it's not via AJAX
                                 headers = {'X-Requested-With' : 'XMLHttpRequest'},
                                 credentials=self.credentials,
                                 resp = True,
                                 async = False)

            cookie_string = resp['set-cookie']
            #quick and dirty parsing
            self.session = cookie_string.split(";")[0].split("=")[1]
        return self.session

    def workflows(self):
        content = GET(self.BASE + "workflows",
                      credentials=self.credentials)
        s = cStringIO.StringIO(content)
        p = plistlib.readPlist(s)
        return p['workflows']

    def select_workflow(self,uuid):
        POST(self.BASE + "capture/select_workflow",
             params=dict(selected_workflow=uuid),
             credentials=self.credentials,
             headers={'Cookie' : "_session_id=" + self.get_session() + "; BALANCEID=balancer.mongrel2"},
             async=False)

    def upload_file(self,fileobj,filename,workflow_uuid,title="",description=""):
        # BIG GOTCHA HERE:
        # the workflow is set in a separate request from the upload
        # and state is maintained on the server. 
        # that means that there's a race condition here if two PCP
        # objects with the same session_id try to upload files
        # to different workflows at roughly the same time.
        # if there's any chance at all of that happening, you want to 
        # put some kind of mutex around this method call

        # we have to set the workflow uuid first, in a separate request
        self.select_workflow(workflow_uuid)
        # now we prepare the upload

        test = "restclient!"
        if test == "restclient":
            params = dict(
                title=title,
                workflow_select=workflow_uuid, # probably redundant
                description=description)
            content = POST(self.BASE + "capture/file_upload",
                           params=params,
                           files={'source_file' : 
                                  {'file' : fileobj.read(),
                                   'filename' : filename}},
                           credentials=self.credentials,
    #                       headers={'Cookie' : "_session_id=" + self.get_session() + "; BALANCEID=balancer.mongrel2"},
                           async=False
                           )

        else:
            datagen,headers = multipart_encode((
                    ("title",title),
                    ("workflow_select",workflow_uuid), # probably redundant
                    ("description",description),
                    MultipartParam(name="source_file",fileobj=fileobj,filename=filename)
                ))
            request = urllib2.Request(self.BASE + "capture/file_upload", datagen, headers)

            # set up credentials
            base64string = base64.encodestring("%s:%s" % self.credentials)[:-1]
            request.add_header("Authorization", "Basic %s" % base64string)
            request.add_header("Cookie", "_session_id=" + self.get_session() + "; BALANCEID=balancer.mongrel2")

            # and make the actual POST
            content = urllib2.urlopen(request).read()

if __name__ == "__main__":
    # some simple command line stuff for testing
    username = os.environ.get('ANGELDUST_USERNAME',"")
    password = os.environ.get('ANGELDUST_PASSWORD',"")
    if username == "" or password == "":
        print "you must set ANGELDUST_USERNAME and ANGELDUST_PASSWORD environment variables"
        sys.exit(1)
    
    base_url = os.environ.get('ANGELDUST_BASE_URL',"")
    pcp = PCP(base_url,username,password)

    command = sys.argv[1]
    if command == "list_workflows":
        # ./angeldust.py list_workflows
        for wf in pcp.workflows():
            print wf['uuid'],wf['title']
    elif command == "upload_file":
        # ./angeldust.py upload_file /path/to/file.py workflow_uuid title description
        filename = sys.argv[2]
        uuid = sys.argv[3]
        title = sys.argv[4]
        description = sys.argv[5]
        pcp.upload_file(open(filename,"rb"),os.path.basename(filename),uuid,title,description)
    else:
        print "unknown command"




