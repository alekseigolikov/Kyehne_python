#!/usr/bin/python
import os
import abc
import urllib
import urllib2
import string
import argparse
import BaseHTTPServer

"""

    Examples of usage of this module:

Standalone server storing shiping information locally in predefined root path.
python task.py -M server -H localhost -p 8800 -r "c:\temp\\" -m 'some_string_that_trigger_shutdown'

Proxy server requesting shiping information from another server, url is defined  with root path key.
python task.py -M proxy -H localhost -p 8811 -r "http://localhost:8800/" -m 'some_string_that_trigger_shutdown'

CLI tool to query servers using API queies passed in query parameter.
python task.py -M cli -H localhost -p 8800 -q "create 12312312312 Destination=Hamburg\nSender=Tallinn\nState=Sent"
python task.py -M cli -H localhost -p 8800 -q "update 12312312312 Destination=Hamburg\nSender=Tallinn\nState=Delivered"

Testing of API class
python task.py -M test -H localhost -p 9979 -r "c:\prog\temp\"
C:\Users\algoliko\Desktop>python task.py -M test -H localhost -p 9979 -r "c:\prog\temp\\"


    Expected Testing output:

Testing file Layer
Running test: List empty list of shipments - Expected 404/Received 404  RESULT: OK
Running test: Creation of new shipment record - Expected 200/Received 200  RESULT: OK
Running test: Creation of already existant shipment record - Expected 409/Received 409  RESULT: OK
Running test: List of available shipments - Expected 200/Received 200  RESULT: OK
Running test: Retrieve content of existant shipment record - Expected 200/Received 200  RESULT: OK
Running test: Retrieve content of non existant shipment - Expected 404/Received 404  RESULT: OK
Running test: Update of existant shipment - Expected 200/Received 200  RESULT: OK
Running test: Update of non existant shipment - Expected 404/Received 404  RESULT: OK
Running test: Drop record of existant shipment - Expected 200/Received 200  RESULT: OK
Running test: Drop record of non existant shipment - Expected 404/Received 404  RESULT: OK
Running test: Issuing unknow command - Expected 400/Received 400  RESULT: OK
Testing http Layer
Running test: List empty list of shipments - Expected 404/Received 404  RESULT: OK
Running test: Creation of new shipment record - Expected 200/Received 200  RESULT: OK
Running test: Creation of already existant shipment record - Expected 409/Received 409  RESULT: OK
Running test: List of available shipments - Expected 200/Received 200  RESULT: OK
Running test: Retrieve content of existant shipment record - Expected 200/Received 200  RESULT: OK
Running test: Retrieve content of non existant shipment - Expected 404/Received 404  RESULT: OK
Running test: Update of existant shipment - Expected 200/Received 200  RESULT: OK
Running test: Update of non existant shipment - Expected 404/Received 404  RESULT: OK
Running test: Drop record of existant shipment - Expected 200/Received 200  RESULT: OK
Running test: Drop record of non existant shipment - Expected 404/Received 404  RESULT: OK
Running test: Issuing unknow command - Expected 400/Received 400  RESULT: OK


    Protocol description:

    All commands are passed in URL, some commands have parameters
URL have format of: http://hostname/command/parameters
some commands requere to post data with raw post
    
    
    List command
-list - listing of all awailable shiping documents
:example    list
:arguments  0
:method     GET
:status_codes:
    200 - OK
    404 - No documents found
:status_text:
    list of documents delimited with line feed: (200, 'new_document_1\nnew_document_2')
    error description:                          (404, 'No documents found')
    
    
    Retrieve command
-retrieve - retrival content of particular document
:example    retrieve/new_document_1
:arguments  1 - name of document
:method     GET
:status_codes:
    200 - OK
    404 - Document not found
:status_text:
    error description   (404, 'Document not found')
    file content        (200, 'sender=me\\nreceiver=you\\nstatus=sent')
        
        
    Delete command
-delete  - delete of particular document
:example    delete/new_document_1
:arguments  1 - name of document
:method     GET
:status_codes:
    200 - OK
    404 - Document not found
:status_text:
    error_description  (404, 'Document not found')
    result              (200, 'OK')
    
    
    Create command
-create    - command to create new shipping document
             its expected that document will have format of key values pairs delimited with equal sign
             all pairs are separated with line feed sign
            
:example     create/new_document_2 
:post part - sender=me\nreceiver=you\nstatus=sent
:arguments  2 - name of document passed in URL
              - file content passed with raw post
              
:status_codes:
    200 - OK
    409 - Already exist
:status_text:
    error description   (409, 'Aready exists')
    result              (200, 'OK')
    
    
    Update command
-update    - command to update/add new key-val pairs to document
:example     update/new_document_2 
:post part - status=delivered
:arguments  2 - name of document passed in URL
              - pairs to be replaced/added
              
:status_codes:
    200 - OK
    404 - No such document
:status_text:
    error description   (404, 'Document not found')
    result              (200, 'Completed successully')
    

"""


class CommAbsClass(object):
    """
        Abstract class which which define necessary interfaces for data acess
    """
    __metaclass__ = abc.ABCMeta
    
    def __init(self, address):
        self._address = address
    
    @abc.abstractmethod
    def check_connection(self):
        """"create connection"""
        return
    
    @abc.abstractmethod
    def do_POST(self, *params):
        """"create connection"""
        return
    
    @abc.abstractmethod
    def do_GET(self, *params):
        """"create connection"""
        return

        
class HTTPLayer(CommAbsClass):
    """
        Class intended to provide acess to data stored remotelly
    """
    def __init__(self, address):
        self._address = address
        
    def check_connection(self):
        pass
        
    def do_POST(self, action, *params):
        update_id = params[0]
        update_doc = params[1]
        url = self._prepare_url(action, update_id)
        reqObj = urllib2.Request(url, update_doc)
        reqObj.add_header('Content-Length', '%d' % len(update_doc))
        reqObj.add_header('Content-Type', 'application/html')
        try:
            resObj = urllib2.urlopen(reqObj)
            status_code = resObj.getcode()
            status_text = resObj.read()
        except (urllib2.URLError) as err:
            if hasattr(err, 'getcode'):
                status_code = err.getcode()
                status_text = err.read()
            else:
                return(500, err.reason)
        return(status_code,status_text) 
        
        
    def do_GET(self, action, *params):        
        url = self._prepare_url(action, *params)
        try:
            reqObj = urllib2.Request(url)
            resObj = urllib2.urlopen(reqObj) 
            status_text = resObj.read()
            status_code = resObj.getcode()
        except (urllib2.URLError) as err:
            if hasattr(err, 'getcode'):
                status_code = err.getcode()
                status_text = err.read()
            else:
                return(500, err.reason)
        return(status_code, status_text)

    def _prepare_url(self, action, *params):
        url = self._address.__add__('/{0}'.format(action))
        if(params):
            url = url.__add__('/{0}'.format(params[0]))
        return url
         
class FileLayer(CommAbsClass):
    """
        Class intended to provide acess to data stored locally
    """    
    def __init__(self, address):
        self._address = address
        
    def check_connection(self):
        return os.path.exists(self._address)
    
    def do_POST(self, action, *params):
        file_name = params[0]
        if action == 'create':
            if(self._file_exists(file_name)):
                return(409,'Aready exists')
            return self._put_file_content(*params)
        if(self._file_exists(file_name)):
            return self._update_file_content(*params)
        return (404,'Document not found')

    def do_GET(self, action, *params):
        if(action in ('list','magic_string')):
            (status_code, status_text) = self._get_dir_list()
            if type(status_text) is list:
                status_text = string.join(status_text,'\n')
            return (status_code, status_text)
        file_name = params[0]
        if(action == 'retrieve' and self._file_exists(file_name)):
            return self._get_file_content(file_name)
        if(action == 'delete' and self._file_exists(file_name)):
            return self._drop_file(file_name)
        return (404,'Document not found')
        
    def _put_file_content(self, *params):
        file_name = params[0]
        file_content = params[1]
        try:
            with open(self._address.__add__(file_name), 'w') as fh:
                fh.write(file_content)
        except IOError as err:
            return(500, 'Internal Error: {0}'.format(err.strerror))
        return(200, 'Completed successully')
        
    def _file_exists(self, *params):
        file_name = params[0]
        return os.path.exists(self._address.__add__(file_name))
    
    def _drop_file(self, *params):
        file_name = params[0]
        status_code = 200
        status_text = "OK"
        try:
            os.remove(self._address.__add__(file_name))
        except OSError as err:
            return(500, 'Internal Error: {0}'.format(err.strerror))
        return (status_code, status_text) 
    
    def _update_file_content(self, *params):
        file_name = params[0]
        content_new = params[1]
        content_old = self._get_file_content(file_name)[1]
        try:
            content_new = self._update_content(content_old, content_new)
        except Exception as err:
            return(415, 'incorrect data format')
        return self._put_file_content(file_name, content_new)
        
    def _get_dir_list(self):
        try:
            out = os.listdir(self._address)
            if out.__len__() == 0:
                return(404, 'No documents found')
            return(200, out)
        except IOError as err:
            return(500, 'Internal Error: {0}'.format(err.strerror))
            
    def _get_file_content(self, file_name):
        out = ''
        try:
            with open(self._address.__add__(file_name)) as fh:
                for line in fh:
                   out = out.__add__(line)
                return(200,out)
        except IOError as err:
            return(404, 'Internal Error: {0}'.format(err.strerror))
            
    def _update_content(self, text_orig, text_change):
        out=''
        tdir={}
        
        if text_orig.__len__()==0:
            return text_change
        if text_change.__len__()==0:
            return ''
        for line in text_orig.split('\n'):
            (key, val) = line.split('=',1)
            tdir[key] = val
        for line in text_change.split('\n'):
            (key, val) = line.split('=',1)
            tdir[key] = val
        for key, val in tdir.iteritems():
            out = out.__add__('{0}={1}\n'.format(key, val))
        return out
        
            
class WebAPI(object):
    """
        API class providing support to protocol and access to data using different layers: http and file
    """
    
    def __init__(self, address, env = None):
        """
            constructor storing addres/location of data along with method to access it
                :param address: Adress in case of http layer/Directory in case of file layer
                :param env: type of access to data http/file
        """
        if (env is None) or (type(env) is not str) or (env not in ['http','file']):
            return(500, 'Internal Error')
        if env == 'http':
            self._connector = HTTPLayer(address)
        else:
            self._connector = FileLayer(address)
        
        """ 
            dictionary holding: 
            :param key: list of supported command along with 
            :param handler: handler and 
            :param argc: ammount of required parameters 
        """
        self.lookup = {'list'        :{'handler': self._connector.do_GET, 'argc': 0}, 
                       'retrieve'    :{'handler': self._connector.do_GET, 'argc': 1},
                       'delete'      :{'handler': self._connector.do_GET, 'argc': 1},
                       'magic_string':{'handler': self._connector.do_GET, 'argc': 1},
                       'create'      :{'handler': self._connector.do_POST,'argc': 2},
                       'update'      :{'handler': self._connector.do_POST,'argc': 2},
                       }

    def do_action(self, action, *params):
        """
            Method to invoke handler for partcular command
            :param action: API command name
            :param params: structure holding parameter and values
        """
        status_code = 501
        status_text = 'Internal Error'
        try:
            if(params.__len__() == self.lookup[action]['argc']):
                (status_code,status_text) = self.lookup[action]['handler'](action, *params)
            else:
                raise KeyError('Bad Request')
        except (KeyError, IndexError) as err:
           status_code = 400
           status_text = 'Bad Request for {0}'.format(action)
        return(status_code, status_text)    


class CLIClass(object):
    """
        Class for implementing CLI functionaliy acess manually server to make troubleshooting
    """
    def __init__(self, *params):
        """
            Constructor storing necessary stuff in attributes:
            :param query: command to send to server
            :param host: hostname of server
            :param port: port
        """
        settings = params[0]
        self.query = settings['query']
        self.host  = settings['host']
        self.port  = settings['port']
        self.path  = settings['path']
        self.magic_string = settings['magic_string']
    #aleksei vernutsja sjuda
    def do_action(self):
        query = self.query.split(' ', 2)
        # here we create our API object
        rest_object = WebAPI('http://' + self.host + ':' + self.port + '/' ,'http')
        command = query.pop(0)
        if(query.__len__() == 1):
            return rest_object.do_action(command, query[0])
        if(query.__len__() == 2):
            return rest_object.do_action(command, query[0], query[1])
        if(query.__len__() == 0):
            return rest_object.do_action(command)
            
class ServerClass(BaseHTTPServer.HTTPServer):
    """
        Server class inherits from httpserver class, 
        overloading constructor in order to store some specific info
        intended to be used for server instance creation
    """
    def __init__(self, *args, **kwargs):
        """
            :param keep_going: Boolean value defining should server continue to run or stop
            :param root_path: root path if server / address of another hop if proxy
            :param data_source: data access type defining protocol of accessing data local or remote
        """
        (settings, handlerObj) = args
        BaseHTTPServer.HTTPServer.__init__(self, (settings['host'], int(settings['port'])), handlerObj)
        self.keep_going = settings['keep_going']
        self.root_path = settings['root_path']
        self.magic_string = settings['magic_string']
        if settings['mode'] == 'server':
            self.data_source = 'file'
        else:
            self.data_source = 'http'

class RequestsHandlerClass(BaseHTTPServer.BaseHTTPRequestHandler):
    """
        Handler hlass for http server holding scenarios for answers generation
    """
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _parse_path(self, lookup):
        """
            supplementary method to parse request and get command and parameter from url,
            assuming that commant is last word from right side delimited by / which named key exist in lookup attribute
            http://somehost:someport/some/path/to/command/parameter
        """
        path_pieces = self.path.split('/')
        prev_piece = ''
        while path_pieces:
            curr_piece = path_pieces.pop()
            if curr_piece in lookup:
                return(curr_piece, prev_piece)
            prev_piece = curr_piece
        return(curr_piece, prev_piece)

    def do_GET(self):
        """Handler for GET requests"""
        status_code = 500
        status_text = "Internal Error"
        # here we create our API object
        rest_object = WebAPI(self.server.root_path,self.server.data_source)
        lookup = rest_object.lookup.keys()
        (get_command, get_param) = self._parse_path(lookup)
        if get_command == 'list':
            (status_code, status_text) = rest_object.do_action(get_command)
        else:
            (status_code, status_text) = rest_object.do_action(get_command, get_param)
        if self.server.magic_string is not None:
            if self.path.find(self.server.magic_string) > -1:
                self.server.keep_going = False
                status_code = 201
                status_text = "Shuting down"
        self.send_response(status_code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(status_text)
        
    def do_POST(self):
        """Handler for POST requests"""
        raw_post = self.rfile.read(int(self.headers.getheader('Content-Length')))
        status_code = 500
        status_text = "Internal Error"
        # here we create our API object
        rest_object = WebAPI(self.server.root_path,self.server.data_source)
        lookup = rest_object.lookup.keys()
        (get_command, get_param) = self._parse_path(lookup)
        (status_code, status_text) = rest_object.do_action(get_command, get_param, raw_post)
        self.send_response(status_code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(status_text)
        
class TestClass(object):
    """
        Class intended to test some scenarios of accessing data using WebAPI class
        using both ways to access data local and remote
    """
    def __init__(self, *params):
        settings = params[0]
        self.query = settings['query']
        self.host  = settings['host']
        self.port  = settings['port']
        self.path  = settings['path']
        self.magic_string = settings['magic_string']
    
    def do_action(self, *params):
        layer_type = params[0]
        
        if layer_type == 'http':
            data_source = 'http://' + self.host + ':' + self.port + '/'
        else:
            data_source = self.path
        """
            Dictionary holding testing scenarious wiht expectng results
            :param name: test description
            :param params: params passed to API
            :param result: expected result
        """
        test_list = ({'name':'List empty list of shipments',
                       'params':['list',()],
                       'result':404
                     },
                     {'name':'Creation of new shipment record',
                       'params':['create',('a123','test=test\nhophop=tata')],
                       'result':200
                     },
                     {'name':'Creation of already existant shipment record',
                       'params':['create',('a123','test=test\nhophop=tata')],
                       'result':409
                     },
                     {'name':'List of available shipments',
                       'params':['list',()],
                       'result':200
                     },
                     {'name':'Retrieve content of existant shipment record',
                       'params':['retrieve',('a123',)],
                       'result':200
                     },
                     {'name':'Retrieve content of non existant shipment',
                       'params':['retrieve',('a456',)],
                       'result':404
                     },
                     {'name':'Update of existant shipment',
                       'params':['update',('a123','test=2')],
                       'result':200
                     },
                     {'name':'Update of non existant shipment',
                       'params':['update',('b543','test=2')],
                       'result':404
                     },
                     {'name':'Drop record of existant shipment',
                       'params':['delete',('a123',)],
                       'result':200
                     },
                     {'name':'Drop record of non existant shipment',
                       'params':['delete',('b456',)],
                       'result':404
                     },
                     {'name':'Issuing unknow command',
                       'params':['one',('beer','please')],
                       'result':400
                     },)
                     
        
        #creating of API object
        test_object = WebAPI(data_source, layer_type)
        os.sys.stdout.write('Testing {0} Layer\n'.format(layer_type))
        #testing loop
        for test in test_list:
            result = 'OK'
            os.sys.stdout.write('Running test: {0}'.format(test['name'])) 
            command = test['params'].pop(0)
            params = test['params'].pop(0)
            (status_code, status_text) = test_object.do_action(command, *params)
            os.sys.stdout.write(' - Expected {0}/Received {1} '.format(test['result'], status_code))
            try:
                assert(test['result'] == status_code)
            except AssertionError as err:
                result = 'FAILED'
            os.sys.stdout.write(' RESULT: {0}\n'.format(result))
             
               
                
if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage = 'Usage: %(prog)s -M <mode> -p <port> -h <host> [options] -r <root_path>')
    parser.add_argument('-M', dest='mode', action='store', help='Mode to run, possible values: ''server'',''cli'',''proxy'',''test''', default = 'server')
    parser.add_argument('-H', dest='host', action='store', help='Host to listen/interact to', default = 'localhost')
    parser.add_argument('-p', dest='port', action='store', help='Port to listen/interact to', default = '9979')
    parser.add_argument('-r', dest='root_path', action='store', help='Path where documents are stored, in proxy mode it holds url of main server', default = 'C:\\temp\\')
    parser.add_argument('-q', dest='query', action='store', help='query string example:''retrieve 123''', default = 'list')
    parser.add_argument('-m', dest='magic_string', action='store', help='Magic string sent as query will lead to stop server', default = 'StopServerNow')
    opts = parser.parse_args()
    
    if opts.mode in ('server', 'proxy'):
        server_object = ServerClass(({'host':opts.host, 'port':opts.port, 'keep_going': True, 'root_path':opts.root_path, 'mode':opts.mode, 'magic_string':opts.magic_string}), RequestsHandlerClass)
        print 'Starting Up server'
        while(server_object.keep_going):
            server_object.handle_request()
        print 'Stoping server'
        server_object.server_close()
    
    if opts.mode == 'cli':
        cli_object = CLIClass({'host':opts.host,'port':opts.port,'path':opts.root_path,'query':opts.query, 'magic_string':opts.magic_string})
        print cli_object.do_action()
        
    if opts.mode == 'test':
        test_object = TestClass({'host':opts.host,'port':opts.port,'path':opts.root_path,'query':opts.query, 'magic_string':opts.magic_string})
        test_object.do_action('file')
        test_object.do_action('http')

    
