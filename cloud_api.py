import urllib.request, urllib.error, urllib.parse, json, threading, os, queue, logging
from multipart import MultiPartForm
from urllib.parse import urlparse

class RequestWithMethod(urllib.request.Request):
    """Workaround for using DELETE with urllib2"""
    def __init__(self, url, method, data=None, headers={},\
        origin_req_host=None, unverifiable=False):
        self._method = method
        urllib.request.Request.__init__(self, url, data=None, headers={},\
                 origin_req_host=None, unverifiable=False)

    def get_method(self):
        return self._method
    
class CloudApi(object):
    """Asynchronus multithreaded library interfacing with the cloudapp api"""
    
    apiUrl = "http://my.cl.ly"
    _queue = queue.Queue()
    uploadQueue = queue.Queue()
    
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
        authHandler = urllib.request.HTTPDigestAuthHandler()
        authHandler.add_password("Application", "my.cl.ly", username, password)
        opener = urllib.request.build_opener(authHandler)
        urllib.request.install_opener(opener)
        
    def getFileList(self, maxItems, callback):
        req = urllib.request.Request(self.apiUrl + '/items?page=1&per_page=' + str(maxItems))
        req.add_header('Accept', 'application/json')
        self._queue.put((req, callback))
        
    def bookmark(self, url, callback = None):
        req = urllib.request.Request(self.apiUrl + '/items')
        req.add_header('Accept', 'application/json')
        req.add_header('Content-Type', 'application/json')
        name = urlparse(url).netloc
        req.add_data(('{"item":{"name":"%s","redirect_url":"%s"}}' % (name,url)).encode('utf-8'))
        self._queue.put((req, callback))

    def uploadFile(self, url, callback = None):
        self.uploadQueue.put((url, callback))
    
    def delete(self, url, callback = None):
        req = RequestWithMethod(url, 'DELETE')
        req.add_header('Accept', 'application/json')
        self._queue.put((req, callback))
    
    class ApiThread(threading.Thread):
            
        def run(self):
            while True:
                task = CloudApi._queue.get()
                if task:
                    try:
                        pagehandle = urllib.request.urlopen(task[0])
                        self.data = json.loads(pagehandle.read().decode('utf-8'))
                        if task[1]:
                            task[1](self.data)
                    except urllib.error.HTTPError as e:
                        logging.error("HTTP Error Code:" + str(e.code))
                    except urllib.error.URLError as e:
                        logging.error(e.reason)
            
    class UploadThread(threading.Thread):
        
        def getUploadParams(self):
            req = urllib.request.Request('http://my.cl.ly/items/new')
            req.add_header('Accept', 'application/json')
            response = urllib.request.urlopen(req)
            return json.loads(response.read().decode('utf-8'))
            
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
                                form.addField(name, uploadParams["params"][name])
                            
                            filePath = urlparse(self.url).path
                            # fp = open(filePath, 'rb')
                            form.addFile(filePath)
                            # form.addFile("file",os.path.basename(filePath) , fp)
                            body = form.toBytes()

                            req = urllib.request.Request(uploadParams["url"])
                            req.add_header('Content-type', form.getContentType())
                            req.add_header('Content-length', str(len(body)))
                            req.add_header('Accept', 'application/json')
                            req.add_data(body)
                            response = urllib.request.urlopen(req)
                            if self.callback:
                                self.callback(json.loads(response.read().decode('utf-8')))
                        except urllib.error.HTTPError as e:
                            logging.error("HTTP Error Code:" + str(e.code))
                        except urllib.error.URLError as e:
                            logging.error(e.reason)
                        except IOError as e:
                            logging.error("IOError when opening file to upload: "+filePath)
           
