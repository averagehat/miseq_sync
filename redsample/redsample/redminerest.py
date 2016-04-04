#!/usr/bin/env python

import json
import urllib2
import urllib

from redsample.defaults import defaults

class HttpError(Exception):
    def __str__( self ):
        return "{}: {}".format(self.message,self.__dict__.get('errors',''))

# Generic exception for duplicate entry
class DuplicateEntry(HttpError):
    dupissue = None
class RelationExists(HttpError): pass
class FieldValidationError(HttpError): pass
class BadQuery(HttpError): pass
class InvalidIssue(HttpError): pass

class RedmineREST(object):
    def __init__( self, url, key ):
        self.key = key
        self.url = url
        self.headers = {'Content-Type': 'application/json', 'X-Redmine-API-Key':self.key}

    def do_get_request( self, url ):
        req = self.make_request( url, headers=self.headers )
        res = self.do_request( req )
        return self.parse_jsons( res.read() )

    def make_request( self, url, **kwargs ):
        return urllib2.Request( url, **kwargs )

    def handle_httperror( self, httperror, req ):
        if httperror.code == 422:
            self.handle_422( httperror, req )
        elif httperror.code == 404:
            self.handle_404( httperror, req )
        else:
            raise httperror

    def handle_422( self, httperror, req ):
        raise httperror

    def handle_404( self, httperror, req ):
        raise httperror

    def do_request( self, req ):
        try:
            return urllib2.urlopen( req )
        except urllib2.HTTPError as e:
            # Do better handling
            self.handle_httperror( e, req )
        except Exception as e:
            # Don't know what this is
            raise e

    def parse_jsons( self, jsons ):
        import json
        return json.loads( jsons )

class RedSamples( RedmineREST ):
    # Someday replace this with defaults stuff
    SEQUENCE_REQUEST_PROJECT_ID = defaults['SEQUENCE_REQUEST_PROJECT_ID']
    SAMPLE_PROJECT_ID = defaults['SAMPLE_PROJECT_ID']
    # Tracker id 
    NEW_SAMPLE_TRACKER_ID = defaults['NEW_SAMPLE_TRACKER_ID']
    NEW_SEQUENCE_REQUEST_TRACKER_ID = defaults['NEW_SEQUENCE_REQUEST_TRACKER_ID']
    # Status id
    NEW_SAMPLE_STATUS_ID = defaults['NEW_SAMPLE_STATUS_ID']
    NEW_SEQUENCE_REQUEST_STATUS_ID = defaults['NEW_SEQUENCE_REQUEST_STATUS_ID']
    # Custom fields
    SAMPLELIST_ID = defaults['SAMPLELIST_ID']
    PLATFORM_ID = defaults['PLATFORM_ID']
    SAMPLESSYNCED_ID = defaults['SAMPLESSYNCED_ID']

class Issues( RedSamples ):
    DuplicateEntry = DuplicateEntry
    RelationExists = RelationExists
    FieldValidationError = FieldValidationError
    BadQuery = BadQuery
    InvalidIssue = InvalidIssue

    def handle_422( self, httperror, req ):
        '''
            SampleList error
            Duplicate relation
        '''
        errors = self.parse_jsons( httperror.read() )['errors']
        if 'SampleList' in errors[0]:
            e = self.FieldValidationError()
            e.errors = errors
            e.message = errors[0]
        elif 'can\'t be blank' in errors[0]:
            e = self.BadQuery()
            e.errors = errors[0]
            e.message = 'Bad Query Given'
        else:
            e = self.RelationExists()
            e.errors = errors
            e.message = 'Relationship exists'
        raise e

    def handle_404( self, httperror, req ):
        '''
            No issue exists
        '''
        raise self.InvalidIssue( "No issue exists for req: {}".format(req) )

    def make_issue_payload( self, **kwargs ):
        issue = {k:v for k,v in kwargs.items()}
        payload = {'issue':issue}
        payload = json.dumps( payload )
        return payload

    def make_relation_payload( self, **kwargs ):
        relation = {k:v for k,v in kwargs.items()}
        payload = {'relation':relation}
        payload = json.dumps( payload )
        return payload

    def add_issue( self, **kwargs ):
        url = self.url + '/issues.json'

        payload = self.make_issue_payload( **kwargs )

        dups = self.is_duplicate_issue( kwargs )
        if dups:
            e = Issues.DuplicateEntry("{} is a duplicate subject".format(kwargs['subject']))
            e.dupissue = dups
            raise e

        req = self.make_request( url, data=payload, headers=self.headers )
        res = self.do_request( req )
        return self.parse_jsons( res.read() )['issue']

    def is_duplicate_issue( self, issue ):
        sub = issue['subject']
        ret = []
        ret += self.get_issues( subject=sub )['issues']
        if sub.count('-'):
            ret += self.get_issues( subject=sub.replace('-','_') )['issues']
        if sub.count('_'):
            ret += self.get_issues( subject=sub.replace('_','-') )['issues']
        return ret

    def delete_issue( self, id ):
        url = self.url + '/issues/{}.json'.format(id)
        req = self.make_request( url, headers=self.headers )
        req.get_method = lambda: 'DELETE'
        res = self.do_request( req )
        return res.read()

    def get_issue_by_id( self, id, **kwargs ):
        try:
            id = int(id)
        except ValueError as e:
            raise self.InvalidIssue( "{} is not a valid issue id".format(id) )
        url = self.url + '/issues/{}.json'.format(id)
        if kwargs:
            url += '?'
            for k,v in kwargs.items():
                url += '{}={}'.format(k,v)
        req = self.make_request( url, headers=self.headers )
        res = self.do_request( req )
        iss = self.parse_jsons( res.read() )['issue']
        return iss

    def get_issues( self, **kwargs ):
        url = self.url + '/issues.json'
        if kwargs:
            query = '?' + urllib.urlencode( kwargs )
            url += query
        req = self.make_request( url, headers=self.headers )
        res = self.do_request( req )
        return self.parse_jsons( res.read() )

    def update_issue( self, id, issue ):
        url = self.url + '/issues/{}.json'.format(id)
        req = self.make_request( url, data=self.make_issue_payload( **issue ), headers=self.headers )
        req.get_method = lambda: 'PUT'
        res = self.do_request( req )
        return res.getcode()

    def set_relation( self, issue1, relation_type, issue2, delay=None ):
        url = self.url + '/issues/{}/relations.json'.format(issue1['id'])
        if delay:
            payload = self.make_relation_payload( issue_to_id=issue2['id'], relation_type=relation_type, delay=delay )
        else:
            payload = self.make_relation_payload( issue_to_id=issue2['id'], relation_type=relation_type )
        req = self.make_request( url, data=payload, headers=self.headers )
        res = self.do_request( req )
        return res.getcode()

    def get_relation( self, issue ):
        url = self.url + '/issues/{}/relations.json'.format(issue['id'])
        return self.do_get_request( url )['relations']

class Redmine(RedmineREST):
    def get_statuses( self ):
        url = self.url + '/issue_statuses.json'
        return self.do_get_request( url )['issue_statuses']

    def get_trackers( self ):
        url = self.url + '/trackers.json'
        return self.do_get_request( url )['trackers']
