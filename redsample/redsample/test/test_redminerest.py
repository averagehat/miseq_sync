from common import *

class TestRedmineREST(BaseClass):
    def setUp( self ):
        from redsample.redminerest import Redmine
        self.inst = Redmine( self.URL, self.KEY )

    def test_make_request( self ):
        req = self.inst.make_request( 'http://www.google.com', headers={'Content-Type':'application/json'} )
        eq_( 'application/json', req.headers.get('Content-type') )
        eq_( 'www.google.com', req.get_origin_req_host() )

    @patch('urllib2.urlopen')
    def test_do_request( self, urlopen ):
        req = self.inst.make_request( 'http://www.google.com' )
        r = self.inst.do_request( req )
        urlopen.assert_called_with( req )

class TestIssues(BaseClass):
    def setUp( self ):
        super( TestIssues, self ).setUp()
        from redsample.redminerest import Issues, Redmine
        self.inst = Issues( self.URL, self.KEY )
        self.redinst = Redmine( self.URL, self.KEY )
        # For cleanup
        self.issue_ids_added = []

    def tearDown( self ):
        # Works only if delete is working yay tests
        print self.issue_ids_added
        for id in self.issue_ids_added:
            self.inst.delete_issue( id )

    def _add_test_issue( self, **kwargs ):
        from redsample.redminerest import Issues
        allowdup = kwargs.get('allowdup',True)
        if 'allowdup' in kwargs:
            del kwargs['allowdup']
        kwargs['subject'] = kwargs.get('subject','testsubject')
        kwargs['description'] = kwargs.get('description','testdescription')
        kwargs['project_id'] = kwargs.get('project_id',TEST_PROJECT['id'])
        kwargs['tracker_id'] = kwargs.get('tracker_id',self.tracker_ids['Misc'])
        try:
            # Adds an issue for testing
            iss = self.inst.add_issue( **kwargs )
            print "Adding id {} to be deleted later".format(iss['id'])
            self.issue_ids_added.append( iss['id'] )
            return iss
        except Issues.DuplicateEntry as e:
            if allowdup:
                return self.inst.get_issues( subject=kwargs.get('subject','testsubject') )['issues'][0]
            else:
                raise e

    def test_add_issue( self ):
        # Just check no errors
        self._add_test_issue()
        # Check custom fields too
        self._add_test_issue(
            subject='customfield',
            tracker_id=self.tracker_ids['Sequencing Request'],
            custom_fields=[
                {'id':self.custom_field_ids['SampleList'],'value':'Sample1'},
                {'id':self.custom_field_ids['Platform'],'value':'MiSeq'}
            ]
        )

    def test_issue( self ):
        # Trackers
        trackers = self.redinst.get_trackers()
        # Crappy way of getting Misc tracker id which won't exist unless setup in Redmine....
        tracker_id = [tracker for tracker in trackers if tracker['name'] == 'Misc'][0]['id']

        issue = self._add_test_issue()
        insert_id = issue['id']
        ok_( insert_id > 0 )

        # Get
        get_issue = self.inst.get_issue_by_id( insert_id )
        eq_( insert_id, get_issue['id'] )

        # Update
        uissue = {
            'subject': 'updated-subject'
        }
        eq_( 200, self.inst.update_issue( insert_id, uissue ) )
        updated_issue = self.inst.get_issue_by_id( insert_id )
        eq_( 'updated-subject', updated_issue['subject'], 'Issue did not update' )
        eq_( 'testdescription', updated_issue['description'], 'Updated too many fields' )

        # Delete
        del_issue = self.inst.delete_issue( insert_id )
        eq_( '', del_issue )
        # Unqueue for deletion
        self.issue_ids_added.remove( insert_id )
        import urllib2
        try:
            self.inst.get_issue_by_id( insert_id )
            ok_( False, "Did not remove issue {}".format(insert_id) )
        except urllib2.HTTPError as e:
            pass

    def test_get_issues( self ):
        oiss = self._add_test_issue()
        iss = self.inst.get_issues( subject=oiss['subject'] )['issues'][0]
        eq_( oiss['subject'], iss['subject'] )
        eq_( oiss['id'], iss['id'] )

    def test_is_duplicate_issue( self ):
        iss = self._add_test_issue()
        eq_( True, self.inst.is_duplicate_issue( iss ) )
        iss['subject'] = 'sub'
        eq_( False, self.inst.is_duplicate_issue( iss ) )

    def test_issue_subjects_are_uniq( self ):
        from redsample.redminerest import Issues
        i1 = self._add_test_issue()
        try:
            i2 = self._add_test_issue( subject=i1['subject'], description=i1['description'], allowdup=False )
            ok_( False, "add_issue allowed a duplicate entry" )
        except Issues.DuplicateEntry as e:
            ok_( True )

    def test_relation( self ):
        issue1 = self._add_test_issue(subject='sample_from')
        issue2 = self._add_test_issue(subject='sample_to')
        self.inst.set_relation( issue1, 'blocks', issue2 )
        r1 = self.inst.get_relation( issue1 )[0]
        r2 = self.inst.get_relation( issue2 )[0]
        eq_( r1, r2, 'Relations were not the same' )
        eq_( issue1['id'], r1['issue_id'], 'Did not set relationship id correctly' )
        eq_( issue2['id'], r1['issue_to_id'], 'Did not set relationship to_id correctly' )
        eq_( 'blocks', r1['relation_type'], 'Did not set relationship type correctly' )

    def test_handle_422_samplelist( self ):
        from redsample.redminerest import Issues
        try:
            self._add_test_issue(
                subject='failymcfailerton',
                tracker_id=self.tracker_ids['Sequencing Request'],
                custom_fields=[
                    {'id':self.custom_field_ids['SampleList'],'value':'Sample1_\r\nSample2 space'},
                    {'id':self.custom_field_ids['Platform'],'value':'MiSeq'}
                ]
            )
            ok_( False, 'Did not raise FieldValidationError' )
        except Issues.FieldValidationError as e:
            ok_( True )

    def test_handle_422_relationexist( self ):
        from redsample.redminerest import Issues
        try:
            i1 = self._add_test_issue(subject='relate1')
            i2 = self._add_test_issue(subject='relate2')
            self.inst.set_relation( i1, 'blocks', i2 )
            self.inst.set_relation( i1, 'blocks', i2 )
            ok_( False, 'Did not raise RelationExists' )
        except Issues.RelationExists as e:
            ok_( True )

class TestRedmine(BaseClass):
    def setUp( self ):
        super( TestRedmine, self ).setUp()
        from redsample.redminerest import Redmine
        self.inst = Redmine( self.URL, self.KEY )

    def test_get_statuses( self ):
        statuses = self.inst.get_statuses()
        ok_( isinstance( statuses, list ), 'Returned object not a list' )
        # Just make sure that first item is a status item
        eq_( set(['id','is_default','name']), set(statuses[0].keys()) )

    def test_get_trackers( self ):
        trackers = self.inst.get_trackers()
        ok_( isinstance( trackers, list ), 'Returned object not a list' )
        eq_( set(['id','name']), set(trackers[0].keys()) )
