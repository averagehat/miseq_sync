from common import *

class TestDefaults(object):
    pass

class TestUnitUpdateFrom(TestDefaults):
    def _C( self, *args, **kwargs ):
        from redsample.defaults import update_from_
        return update_from_( *args, **kwargs )

    def test_update_myfile( self ):
        from redsample.defaults import defaults
        url = defaults['URL']
        tfile = 'redsampletest.py'
        d = self._C( tfile )
        ok_( url == d['URL'], 'URL Changed' )
        with open( tfile, 'w' ) as fh:
            fh.write( "config = {'KEY':'ABCD'}" )
        d = self._C( tfile )
        eq_( 'ABCD', d['KEY'], "Did not update defaults" )
        ok_( url != d['KEY'], "URL didn't change" )
        os.unlink( tfile )
