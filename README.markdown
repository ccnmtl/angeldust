Angeldust is a library to interface with Podcast Producer via
Kino's HTTP API

It requires restclient 0.10.1 and a patched version of httplib2 (to
support some weird HTTP Auth headers). I'll make that patch available
soon. 

So far we can: 

* get the list of workflows
* upload a file to a specified workflow

Sample Usage:

    from angeldust import PCP
    pcp = PCP("https://mykinoserver/url/","username","password")
    for workflow in pcp.workflows():
        print "workflow '%s' has UUID %s" % (wf['title'],wf['uuid'])
    pcp.upload_file(open("some_video.avi","rb"),"some_video.avi","uuid-of-workflow","title","description")
