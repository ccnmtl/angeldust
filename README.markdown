Angeldust is a library to interface with Podcast Producer via
Kino's HTTP API

It requires restclient 0.10.1 and a patched version of httplib2 (to
support some weird HTTP Auth headers). I'll make that patch available
soon. 

Look at the bottom of angeldust.py for a quick usage example. 

So far we can: 

* get the list of workflows
* upload a file to a specified workflow


