import urllib2, json, threading, urlparse, os, Queue
from multipart import MultiPartForm

class RequestWithMethod(urllib2.Request):
    """Workaround for using DELETE with urllib2"""
    def __init__(self, url, method, data=None, headers={},\
        origin_req_host=None, unverifiable=False):
        self._method = method
        urllib2.Request.__init__(self, url, data=None, headers={},\
                 origin_req_host=None, unverifiable=False)

    def get_method(self):
        return self._method
    
class CloudApi(object):
    """Asynchronus multithreaded library interfacing with the cloudapp api"""
    
    apiUrl = "http://my.cl.ly"
    queue = Queue.Queue()
    uploadQueue = Queue.Queue()
    
    def __init__(self, username, password):
        self.setLoginDetails(username, password)
        for i in range(3):
            t = self.ApiThread()
            t.setDaemon(True)
            t.start()
        
        t = self.UploadThread()
        t.setDaemon(True)
        t.start()
        
    def setLoginDetails(self, username, password):
        self.userName = username
        self.password = password
        authHandler = urllib2.HTTPDigestAuthHandler()
        authHandler.add_password("Application", "my.cl.ly", username, password)
        opener = urllib2.build_opener(authHandler)
        urllib2.install_opener(opener)
        
    def getFileList(self, maxItems, callback):
        req = urllib2.Request(self.apiUrl + u'/items?page=1&per_page=' + str(maxItems))
        req.add_header('Accept', 'application/json')
        self.queue.put((req, callback))
        
    def bookmark(self, url, callback = None):
        req = urllib2.Request(self.apiUrl + u'/items')
        req.add_header('Accept', 'application/json')
        req.add_header('Content-Type', 'application/json')
        name = urlparse.urlparse(url).netloc
        req.add_data(u'{"item":{"name":"%s","redirect_url":"%s"}}' % (name,url))
        self.queue.put((req, callback))

    def uploadFile(self, url, callback = None):
        self.uploadQueue.put((url, callback))
    
    def delete(self, url, callback = None):
        req = RequestWithMethod(url, 'DELETE')
        req.add_header('Accept', 'application/json')
        self.queue.put((req, callback))
    
    class ApiThread(threading.Thread):
            
        def run(self):
            while True:
                task = CloudApi.queue.get()
                if task:
                    try:
                        pagehandle = urllib2.urlopen(task[0])
                        self.data = json.load(pagehandle)
                        if task[1]:
                            task[1](self.data)
                    except urllib2.HTTPError, e:
                        print "HTTP Error Code:" + str(e.code)
                    except urllib2.URLError, e:
                        print e.reason
            
    class UploadThread(threading.Thread):
        
        def getUploadParams(self):
            req = urllib2.Request('http://my.cl.ly/items/new')
            req.add_header('Accept', 'application/json')
            response = urllib2.urlopen(req)
            return json.load(response)
            
        def run(self):
            while True:
                task = CloudApi.uploadQueue.get()
                if task:
                    self.url, self.callback = task
                    uploadParams = self.getUploadParams()
                    if uploadParams:
                        try:
                            form = MultiPartForm()
                            for name in uploadParams["params"]:
                                form.addField(name.encode('utf8'), uploadParams["params"][name].encode('utf8'))
                            
                            filePath = urlparse.urlparse(self.url).path
                            fp = open(filePath, 'rb')
                            form.addFile("file",os.path.basename(filePath) , fp)
                            body = str(form)

                            req = urllib2.Request(uploadParams["url"])
                            req.add_header('Content-type', form.getContentType())
                            req.add_header('Content-length', str(len(body)))
                            req.add_header('Accept', 'application/json')
                            req.add_data(body)
                            response = urllib2.urlopen(req)
                            if self.callback:
                                self.callback(json.load(response))
                        except urllib2.HTTPError, e:
                            print "HTTP Error Code:" + str(e.code)
                        except urllib2.URLError, e:
                            print e.reason
                        except IOError, e:
                            print "IOError when opening file to upload: "+filePath
           
