# coding: utf8

child_of_relation_type = "child_of"
parent_of_relation_type = "parent_of"

class Attachment:
    """An attachment description"""
    def __init__(self,content,mimetype):
        self.content = content
        self.mimetype = mimetype

def ConvertString( db_str ):
    # Without this, I get failures when trying to print fields from Python script
    # With this it prints wierd characters, but at least it works (and in Tuleap special characters are imported smartly)
    return str(db_str.encode('utf-8'))

class Bug:
    """A bug description"""
    def __init__(self):
        self.project = ""
        self.tracker = ""
        self.summary = ""
        self.description = ""
        self.old_id = ""
        self.status = ""
        # severity from 1 to 9
        self.severity = None
        self.author = ""
        self.owner = ""
        self.attachments = dict()
        self.related_ids = dict()
        self.extra_info = []

    def __repr__(self):
        return self.old_id + " (" + self.project + ") " + self.tracker + " (from " + self.author + ", to " + self.owner + ", " + self.status + ", " + str(self.severity) + ") : " + self.summary + " (" + str(len(self.attachments)) + " attachments(s)) " + str(self.related_ids)

    def setStatus(self, status):
        
        translation_dict = { "Nouveau" : "New", "En cours" : "Open", "Résolu" : "Resolved", "Commentaire" : "Need comment", "Fermé" : "Closed", "Rejeté" : "Rejected" }
        
        if status in translation_dict:
            self.status = translation_dict[status]
        else:
            self.status = status

    def setSeverityFromText(self, severity):
        
        translation_dict = { "Bas" : 1, "Normal" : 5, "Haut" : 6, "Urgent" : 8, "Immédiat" : 9 }
        
        if severity in translation_dict:
            self.severity = translation_dict[severity]
        else:
            self.severity = None

    def setSeverityFromValue(self, severity):
        
        if severity >= 0 and severity <= 9:
            self.severity = severity
        else:
            self.severity = None

    def addRelatedIDsToExtraInfo( self ):
        for relation, ids in self.related_ids.items():
            self.extra_info.append( relation + ": [" + ", ".join(ids) + "]" )


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
    