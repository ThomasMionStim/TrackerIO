How to create new plugins?
==========================

# 1. New load plugin

A new "load" plugin will create `Bug` objects from an existing issue tracker.

To create a new plugin, simply create a new "loadplugin_\<your plugin name\>.py" in trackerIO folder.

You Python script will look like:

```
import argparse
from tracker_io_common import Bug, Attachment

def addArguments( parser ):
    # Add to parser all parameters needed by your plugin as non mandatory

def checkArguments( args ):
    # Check that parameters you really need to run are specified, if not return False, else return True

def loadBugs( args ):
    # Load issues from the source tracker and return them as a list of `Bug` objects 
```

Finally, consider adding "loadplugin_\<your plugin name\>.md" with the same sort of content as the extsing ones.

# 2. New save plugin

A new "save" plugin will store `Bug` objects into an existing issue tracker.

To create a new plugin, simply create a new "saveplugin_\<your plugin name\>.py" in trackerIO folder.

You Python script will look like:

```
import argparse
from tracker_io_common import Bug, Attachment

def addArguments( parser ):
    # Add to parser all parameters needed by your plugin as non mandatory

def checkArguments( args ):
    # Check that parameters you really need to run are specified, if not return False, else return True

def saveBugs( args, bugs ):
    # Save issues (list of `Bug` passed as `bugs` argument) in the target tracker 
```

Finally, consider adding "saveplugin_\<your plugin name\>.md" with the same sort of content as the extsing ones.