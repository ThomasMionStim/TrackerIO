from tracker_io_common import Bug, Attachment, child_of_relation_type, parent_of_relation_type

def addArguments( parser ):
    return    

def checkArguments( args ):
    return True

def loadBugs( args ):
    
    bug1 = Bug()
    bug1.summary = "Hello1"
    bug1.description = "Bla bla bla"
    bug1.old_id = "#1"
    bug1.status = "New"
    bug1.author = "jp225611"
    bug1.owner = "toto"
    
    bug2 = Bug()
    bug2.summary = "Hello2"
    bug2.description = "Bla bla bla"
    bug2.old_id = "#2"
    bug2.status = "Duplicate"
    bug2.author = "foo"
    bug2.owner = "jp225611"

    # Add some relations:
    bug1.related_ids[child_of_relation_type] = [bug2.old_id]
    bug2.related_ids[parent_of_relation_type] = [bug1.old_id]

    # Add some attachments:
    with open("welldone.png","rb") as handle:
        bug2.attachments["welldone.png"] = Attachment( handle.read(), "image/png")
    bug2.attachments["helloworld.txt"] = Attachment( "Hello World!".encode(), "text/plain")

    return [ bug1, bug2 ]