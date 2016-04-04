from mock import Mock, patch, MagicMock
from nose.tools import eq_, ok_, raises, timed
from nose.plugins.attrib import attr

import tempfile
from os.path import *
import sys
import os

TEST_PROJECT = {
    'id': 20,
    'name': 'Redmine Samples',
    'identifier': 'redsampletest',
}


from StringIO import StringIO
issue_template = {
    'issue': {'status': {'id':1, 'name':'New'}},
    'priority': {'id':1,'name':'Normal'},
    'author': {'id':1,'name':'User'},
    'start_date': '1979-01-01',
    'project': {'id':1,'name':TEST_PROJECT['name']},
    'created_on': '1979-01-01T01:01:01Z',
    'tracker': {'id':1,'name':'Sample'},
    'updated_on': '1979-01-01T01:01:01Z',
    'id': 0,
    'done_ration': 0,
    'subject': '',
    'description': '',
    'category': '',
    'spent_hours': 0.0
}


class Base(object):
    curid = 0
    db = {}
    KEY = '4d77ffe7370a38688647c9a614a874787a77d922'
    URL = 'http://wrairvdb.herokuapp.com'

    def setUp(self):
        Base.curid = 0
        Base.db = {
            'issues': {},
            'issue_statuses': [
                {'id':1,'name':'New','is_default':True},
                {'id':4,'name':'Sequencing','is_default':False},
                {'id':6,'name':'Completed','is_default':False},
            ]
        }

    def tearDown(self):
        pass

    @classmethod
    def urlopen( klass, request ):
        import json
        import copy
        import re
        import urllib2
        from urlparse import urlparse, parse_qs, parse_qsl
        parsed_url = urlparse( request.get_full_url() )
        if request.get_method() == 'POST':
            klass.curid += 1
            issue = json.loads(request.get_data())['issue']
            proj = issue['project_id']
            iss = copy.deepcopy( issue_template )
            iss['project']['name'] = proj
            iss['subject'] = issue['subject']
            iss['description'] = issue['description']
            iss['id'] = klass.curid
            # New issue
            klass.db['issues'][klass.curid] = iss
            iss = {'issue':iss}
        if request.get_method() == 'PUT':
            id = int( re.search( '/(\d+).json', parsed_url.path ).group(1) )
            query = parse_qsl( parsed_url.query )
            klass.db['issues'][id].update( **request.get_data()['issue'] )
            iss = {}
        if request.get_method() == 'GET':
            if parsed_url.path == '/issues.json':
                iss = {'issues': []}
                query = parse_qsl( parsed_url.query )
                for id,issue in klass.db['issues'].items():
                    # loop through all keys and values and check equality
                    # at the first found one that doesn't match, break and look at next issue
                    found=True
                    for k,v in query:
                        cv = issue.get(k,None)
                        print "CV: {} V: {}".format(cv,v)
                        if cv != v:
                            found=False
                            break
                    if not found:
                        continue
                    # Break as soon as we find the issue
                    iss = {'issues':[issue]}
                    break
            else:
                m = re.findall( '/(\d+).json', parsed_url.path )[0]
                id = int(m)
                try:
                    iss = {'issue':klass.db['issues'][id]}
                except KeyError:
                    e = urllib2.HTTPError(request.get_full_url(), 404, 'Does not exist', request.headers, fp=None )
                    raise e
        if request.get_method() == 'DELETE':
            m = re.findall( '/(\d+).json', parsed_url.path )[0]
            id = int(m)
            del klass.db['issues'][id]
            return StringIO('')

        return StringIO(json.dumps(iss))

class BaseClass(Base):
    def setUp( self ):
        super(BaseClass, self ).setUp()
        self.tracker_ids = {
            'Misc': 5,
            'Sequencing Request': 4,
            'Sample': 6
        }
        self.custom_field_ids = {
            'SampleList': 4,
            'Platform': 5,
            'SamplesSynced': 6
        }

