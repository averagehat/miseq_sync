from common import *

class TestSamples(BaseClass):
    def setUp( self ):
        super( TestSamples, self ).setUp()
        from redsample.samples import Samples
        self.inst = Samples( self.URL, self.KEY )
        self.remove_queue = []

    def tearDown( self ):
        for issue in self.remove_queue:
            try:
                self.inst.delete_issue( issue['id'] )
            except Exception:
                pass

    def test_get_or_create( self ):
        # Clean up
        created,issue = self.inst.get_or_create( 'test-sample' )
        self.remove_queue.append( issue )
        eq_( True, created )
        created1,issue1 = self.inst.get_or_create('test-sample' )
        self.remove_queue.append( issue1 )
        eq_( False, created1 )
        eq_( issue['id'], issue1['id'], "Two Sample issues were created instead of only 1" )
