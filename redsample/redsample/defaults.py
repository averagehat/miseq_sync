from os.path import *
from importlib import import_module
import sys

defaults = dict(
    URL = 'https://vdbpm.org',
    EMAIL_ADDRESS = '',
    EMAIL_PASSWORD = '',
    SEQUENCE_REQUEST_PROJECT_ID = 1,
    SAMPLE_PROJECT_ID = 18,
    # Tracker id 
    NEW_SAMPLE_TRACKER_ID = 6,
    NEW_SEQUENCE_REQUEST_TRACKER_ID = 4,
    # Status id
    NEW_SAMPLE_STATUS_ID = 1,
    NEW_SEQUENCE_REQUEST_STATUS_ID = 1,
    # Custom fields
    SAMPLELIST_ID = 4,
    PLATFORM_ID = 5,
    SAMPLESSYNCED_ID = 6,
    PRNAME_ID = 19,
    # Systems Administrator Group ID
    SYSADMIN_GROUP_ID = 33
)

def update_from_( myfile ):
    if exists( myfile ):
        mod = basename( myfile ).replace('.py','')
        mod = import_module( mod )
        defaults.update( **mod.config )
    return defaults

my = 'my.py'
if not exists(my):
    sys.path.insert( 0, dirname(__file__) )
    my = join( dirname( __file__ ), 'my.py' )
update_from_( my )
