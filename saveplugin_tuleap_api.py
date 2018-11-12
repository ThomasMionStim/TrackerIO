# coding: utf8

import argparse
import getpass
import os
import base64
import datetime
from tracker_io_common import Bug, Attachment, sizeof_fmt

def addArguments( parser ):
    parser.add_argument("--tuleap_api_host", metavar="host", type=str, help='Tuleap host')
    parser.add_argument("--tuleap_api_login", metavar="username", type=str, help='Tuleap login')
    parser.add_argument("--tuleap_api_password", metavar="password", type=str, help='Tuleap password (optional)')
    parser.add_argument("--tuleap_api_tracker", metavar="tracker ID", type=int, help='Tuleap tracker ID')

def checkArguments( args ):
    if args.tuleap_api_host == None or args.tuleap_api_host == "":
        print("No Tuleap host specified")
        return False

    if args.tuleap_api_login == None or args.tuleap_api_login == "":
        print("No Tuleap host specified")
        return False

    if args.tuleap_api_password == None or args.tuleap_api_password == "":
        args.tuleap_api_password = getpass.getpass( "Please enter Tuleap password: ")

    if args.tuleap_api_tracker == None or args.tuleap_api_tracker == "":
        print("No Tuleap tracker specified")
        return False

    print( "Will save bugs to " + args.tuleap_api_host )

    return True

def getAttributeValueID( args, attribute_value, fieldMapValues, case_sensitive ):
    possible_values = set()
    for key, value in fieldMapValues.items():
        if case_sensitive:
            if key == attribute_value:
                possible_values.add( value )
        else:
            if key.lower() == attribute_value.lower():
                possible_values.add( value )

    if len(possible_values) == 1:
        return possible_values.pop()
    else:
        return None

def getAttributeValueString( bug, attr ):
    
    value = getattr(bug, attr.bugAttribute)

    if value in attr.fieldInternalMapping:
        value = attr.fieldInternalMapping[value]

    if isinstance(value, (datetime.datetime, datetime.date)):
        value = value.isoformat()

    return value
  
def userWantsToCancel( errors, warnings ):
    if len(errors) != 0:
        print( "\n" + '\n'.join(errors) )
        print( "\n\nBug tracker must be modified to fix above error(s) please consider creating the tracker from Tracker_Tuleap_imported_by_trackerIO.xml" )
        # We force cancellation:
        return True

    if len(warnings) != 0:
        choice = input("\n" + '\n'.join(warnings) + "\nContinue anyway? (y/n)")
        if choice != "y":
            return True
    return False

class AttributeMapping:
    """An attribute mapping description"""

    def __init__(self, bugAttribute, possibleTuleapFieldNames, fieldMandatory, fieldValueMappingMandatory, fieldValueKeySensitive):
        ## Name of the Bug classes's attribute:
        self.bugAttribute = bugAttribute
        ## Possible field names to store value in when importing to Tuleap:
        self.possibleTuleapFieldNames = possibleTuleapFieldNames[:]
        ## Tuleap field ID:
        self.fieldID = None
        ## Tuleap field msut be imported of not?:
        self.fieldMandatory = fieldMandatory
        ## Attribute value mapping to Tuleap (as string) value:
        self.fieldInternalMapping = dict()
        ## Attribute value (as string) mapping to Tuleap field ID value:
        self.fieldValueMapping = dict()
        ## If the Tuleap field ID value could not be found, should we allow the import or not?:
        self.fieldValueMappingMandatory = fieldValueMappingMandatory
        ## Should field value casse be ignored when trying to match value ID?
        self.fieldValueKeySensitive = fieldValueKeySensitive

    def __repr__(self):
        return self.bugAttribute + ", " + str(self.possibleTuleapFieldNames) + ", ID=" + str(self.fieldID) + ", value map=" + str(self.fieldValueMapping)

def saveBugs( args, bugs ):

    import requests
    import json

    ###############################################################
    ## Go through Tuleap authentification
    ###############################################################

    anonymous = ( args.tuleap_api_login == None or args.tuleap_api_login == "" )

    if not anonymous:
        r = requests.post(args.tuleap_api_host + "/api/tokens", json={"username":args.tuleap_api_login, 
                                                                  "password":args.tuleap_api_password}, verify="ca-bundle.crt")

        j = r.json()
        if r.status_code != 201 or 'error' in j:
            print(r.status_code, r.reason)
            print(r.text[:300] + '...')
            return False

        print("Connected to Tuleap")

        user_id = str(j["user_id"])
        token = j["token"]
        if args.verbose:
            print( "User ID:" + user_id )
            print( "Token:" + token )

        headersGet = {'X-Auth-UserId': user_id, 'X-Auth-Token': token}
        headersPost = {'X-Auth-UserId': user_id, 'X-Auth-Token': token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
    else:
        headersGet = {}
        headersPost = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    ###############################################################
    ## Get tracker info and check is has all required fields
    ###############################################################

    r = requests.get(args.tuleap_api_host + "/api/trackers/" + str(args.tuleap_api_tracker), headers=headersGet, verify="ca-bundle.crt")
    tracker_description = r.json()
    if 'error' in tracker_description:
        print( "Failed to find tracker" )
        print( json.dumps(tracker_description,indent=4) )
        return False
                

    if args.verbose:
        print("GET project's trackers result:" + json.dumps(tracker_description, indent=4))

    # Do a simple mapping between Bug attrbutes and Tuleap fields:
    attributesToExport = []
    # Save mapping between Bug's attribute name, possible tracker field names, bool to tell if it must be set or not, field ID and field possible values
    attributesToExport.append( AttributeMapping( 'summary', ['summary'], True, False, False ) )
    attributesToExport.append( AttributeMapping( 'description', ['details'], True, False, False ) )
    attributesToExport.append( AttributeMapping( 'status', ['status_id'], True, True, False ) )
    attributesToExport.append( AttributeMapping( 'tracker', ['original_tracker'], False, False, False ) )

    severityMapping = AttributeMapping( 'severity', ['severity'], True, True, False )
    severityMapping.fieldInternalMapping = { 1 : '1 - Ordinary',
                                             2 : '2',
                                             3 : '3',
                                             4 : '4',
                                             5 : '5 - Major',
                                             6 : '6',
                                             7 : '7',
                                             8 : '8',
                                             9 : '9 - Critical' }
    attributesToExport.append( severityMapping )
    
    # Requires tracker to have this originally_submitted_by field
    attributesToExport.append( AttributeMapping( 'author', ['originally_submitted_by'], True, False, False ) )
    # Requires tracker to have this originally_submitted_on field
    attributesToExport.append( AttributeMapping( 'submit_date', ['originally_submitted_on'], True, False, False ) )
    # Requires tracker to have this originally_owned_by field, optional mapping as user names may not match!
    attributesToExport.append( AttributeMapping( 'owner', ['originally_owned_by'], True, False, False ) )
    # assigned_to, optional mapping as user names may not match!
    attributesToExport.append( AttributeMapping( 'owner', ['assigned_to'], True, False, False ) )
    # old_id, must be imported
    attributesToExport.append( AttributeMapping( 'old_id', ['original_id'], True, False, False ) )
    # import_extra_info, must be present to save any data we could not save somewhere else:
    attributesToExport.append( AttributeMapping( 'extra_info', ['import_extra_info'], True, False, False ) )
    # project name in case we import bugs from different projects:
    attributesToExport.append( AttributeMapping( 'project', ['original_project'], True, False, False ) )
    
    if args.verbose:
        print( "attributesToExport is " + str(attributesToExport) )
    
    for i in range(len(attributesToExport)):

        valueList = attributesToExport[i].possibleTuleapFieldNames
            
        for value in valueList:
            for field in tracker_description['fields']:
                if args.verbose:
                    print(json.dumps(field, indent=4))

                if value == field['name']:

                    if attributesToExport[i].fieldID == None:

                        # Found field!
                        fieldValueMapping = dict()
                        attributesToExport[i].fieldID = field['field_id']
                        if field['values'] != None:
                            for fieldValueMap in field['values']:
                                # save mapping between names and values
                                fieldValueMapping[fieldValueMap['label']] = fieldValueMap['id']

                        attributesToExport[i].fieldValueMapping = fieldValueMapping.copy()

    attachement_field_id = None
    for field in tracker_description['fields']:
        if "attachment" == field['name']:
            attachement_field_id = field['field_id']
    
    if args.verbose:
        print( "attributesToExport: " + str(attributesToExport) )

    # check it has the right fields
    errors = set()
    warnings = set()
    for attr in attributesToExport:
        if attr.fieldID == None:
            message = "Found no Tuleap field to save " + attr.bugAttribute + " value to (looked for " + str(attr.possibleTuleapFieldNames) + ")"
            if attr.fieldMandatory:
                errors.add( message + " (mandatory)" )
            else:
                warnings.add( message + " (optional)" )

    for bug in bugs:
        if len(bug.attachments) > 0:
            if attachement_field_id == None:
                errors.add( "Found no Tuleap field to save attachments" )

    if userWantsToCancel(errors,warnings):
        return False

    ###############################################################
    ## Check fields with enumerated values have the right values available
    ###############################################################

    errors = set()
    warnings = set()
    mapping_info = set()
    used_target_statuses = dict()
    for bug in bugs:
        for attr in attributesToExport:
            if attr.fieldID != None and len(attr.fieldValueMapping) != 0:
                bug_value = getAttributeValueString(bug, attr)
                if bug_value != "":
                    id = getAttributeValueID( args, bug_value, attr.fieldValueMapping, attr.fieldValueKeySensitive )
                    if id == None:
                        error = "No " + attr.bugAttribute + " (" + str(attr.fieldID) + ") field ID available for value \"" + bug_value + "\""
                        if attr.fieldValueMappingMandatory:
                            errors.add( error + " (mandatory)" )
                        else:
                            warnings.add( error + " (optional)" )
                    else:
                        if args.verbose:
                            mapping_info.add( attr.bugAttribute + " field ID for value \"" + bug_value + "\" is " + str(id) )
                        if attr.bugAttribute == "status":
                            used_target_statuses[id] = bug_value

    if args.verbose:
        print( '\n'.join(mapping_info) )

    if userWantsToCancel(errors,warnings):
        return False

    ###############################################################
    ## Check workflow allows to create artifacts with a status different than "New"
    ###############################################################

    errors = set()
    warnings = set()

    allowed_status_upon_creation = set()
    for transition in tracker_description["workflow"]["transitions"]:
        if transition["from_id"] == None:
            allowed_status_upon_creation.add(transition["to_id"])
            if args.verbose:
                print( "ID " + str(transition["to_id"]) + " is accessible for new artifacts" )

    for key,value in used_target_statuses.items():
        if not key in allowed_status_upon_creation:
            errors.add( "New artifacts cannot be created with status \"" + value + "\"" )

    if userWantsToCancel(errors,warnings):
        return False

    ###############################################################
    ## Check size limits
    ###############################################################
    for bug in bugs:

        max_summary_size = 300
        if len(bug.summary) > max_summary_size:
            print( "Summary of " + bug.old_id + " is too long (max size is " + str(max_summary_size) + ")" )
            return False

        for (name, attachment) in bug.attachments.items():
            base64EncodedStr = base64.b64encode(attachment.content)
            file_content = base64EncodedStr.decode("utf-8")

            max_file_size = 1048000
            if len(file_content) > max_file_size:
                print( "Attachment " + name + " of " + bug.old_id + " (size: " + sizeof_fmt( len(file_content) ) + ") is too big (max size is " + sizeof_fmt( max_file_size ) + ") and cannot be imported by current trackerIO version" )
                return False

    ###############################################################
    ## Import bugs
    ###############################################################

    new_ids_map = dict()
    dry_bug_id = 1
    done = 0
    count = len(bugs)
    for bug in bugs:

        ###############################################################
        ## -> Import attachments
        ###############################################################

        attachments_ids = []
        dry_attachment_id = 1
        for (name, attachment) in bug.attachments.items():

            base64EncodedStr = base64.b64encode(attachment.content)
            
            file_content = base64EncodedStr.decode("utf-8")

            json_create_attachement = {
                    "name": name,
                    "mimetype": attachment.mimetype,
                    "content": file_content,
                    "description": ""
                }

            if args.verbose:
                print( "Upload artifact file JSON parameter is\n:" + json.dumps(json_create_attachement,indent=4) )

            if not args.dry:
                r = requests.post(args.tuleap_api_host + "/api/artifact_temporary_files", headers=headersPost, json=json_create_attachement, verify="ca-bundle.crt")
                j = r.json()

                if args.verbose:
                    print("UPLOAD ATTACHEMENT returned:" + json.dumps(j,indent=4))
                if not 'error' in j:
                    print( "Uploaded artifact file " + name + " (id=" + str(j['id']) + ") for " + bug.old_id )
                    attachments_ids.append( j['id'] )
                else:
                    print( "Failed to upload artifact file " + name + " for " + bug.old_id )
                    print( json.dumps(j,indent=4) )
                    return False
            else:
                print( name + " imported as:\n" + json.dumps(json_create_attachement,indent=4) + " resulting fake ID: " + str(dry_attachment_id) )
                attachments_ids.append( dry_attachment_id )
                dry_attachment_id += 1

        ###############################################################
        ## -> Compute extra info to save any data we could not save anywhere else
        ###############################################################
        bug.extra_info = []
        # Save non-mandatory attributes that did not find any matching field:
        for attr in attributesToExport:
            if attr.fieldID == None:
                bug.extra_info.append( attr.bugAttribute + " was " + getAttributeValueString(bug, attr) )

        # As it does not seem obvious to create valid relations iwith REST API, let's just save them as text:
        bug.addRelatedIDsToExtraInfo()

        # convert to string:
        bug.extra_info = "\n".join(bug.extra_info)
                
        ###############################################################
        ## -> Create artifact
        ###############################################################

        field_values = []
        for attr in attributesToExport:
            attr_value = getAttributeValueString(bug, attr)
            if attr.fieldID != None:
                if len(attr.fieldValueMapping) == 0:
                    field_values.append( { "field_id": attr.fieldID, "value": attr_value } )
                else:
                    valueID = getAttributeValueID( args, attr_value, attr.fieldValueMapping, attr.fieldValueKeySensitive )
                    if valueID != None:
                        field_values.append( { "field_id": attr.fieldID, "bind_value_ids": [valueID] } )
                    else:
                        assert not attr.fieldValueMappingMandatory

        if len(attachments_ids) != 0:
            field_values.append( { "field_id": attachement_field_id, "value": attachments_ids } )

        json_create_bug = {
                          "tracker": { "id": args.tuleap_api_tracker },
                          "values": field_values
                          }

        if args.verbose:
            print( "Create artifact JSON parameter is\n:" + json.dumps(json_create_bug,indent=4) )

        if not args.dry:
            # post command if not in test, else, simply show it
            r = requests.post(args.tuleap_api_host + "/api/artifacts", headers=headersPost, json=json_create_bug, verify="ca-bundle.crt")
            j = r.json()
            if args.verbose:
                print("CREATE ARTIFACT returned:" + json.dumps(j,indent=4))
            if not 'error' in j:
                done += 1
                print( "Created artifact " + str(done) + "/" + str(count) + " with Tuleap ID " + str(j['id']) + " for " + bug.old_id + " (" + bug.summary + ")" )
                new_ids_map[bug.old_id] = j['id']
            else:
                print( "Failed to create artifact for " + bug.old_id + " (" + bug.summary + ")" )
                print( json.dumps(j,indent=4) )
                return False
        else:
            print( bug.old_id + " converted as:\n" + json.dumps(json_create_bug,indent=4) + " resulting fake ID: " + str(dry_bug_id) )
            new_ids_map[bug.old_id] = dry_bug_id
            dry_bug_id += 1

    ###############################################################
    ## -> Modify artifact now we know their identifiers
    ###############################################################
    for bug in bugs:
        
        export_field_id = None
        for attr in attributesToExport:
            if attr.bugAttribute == 'extra_info':
                export_field_id = attr.fieldID
                break
        assert not (export_field_id == None)
        
        old_info = bug.extra_info
        for old_id, new_id in new_ids_map.items():
            # Careful, not to convert "relates: [Redmine#1057, Redmine#1058]"
            # into "relates: [Redmine#1 (art #6631)057 (art #6624), Redmine#1 (art #6631)058]"
            for eow in [",","]"]:
                bug.extra_info = bug.extra_info.replace( old_id + eow, old_id + " (art #" + str(new_id) + ")" + eow )

        if old_info != bug.extra_info:
            artifact_id = new_ids_map[bug.old_id]
            json_modify_bug = {
                                  "values": 
                                  [
                                        {
                                            "field_id": export_field_id,
                                            "value": bug.extra_info
                                        }
                                  ]
                              }

            if args.verbose:
                print( "Modify artifact JSON parameter is\n:" + json.dumps(json_modify_bug,indent=4) )

            if not args.dry:
                # post command if not in test, else, simply show it
                r = requests.put(args.tuleap_api_host + "/api/artifacts/" + str(artifact_id), headers=headersPost, json=json_modify_bug, verify="ca-bundle.crt")
                if r.text == "":
                    print( "Modified artifact " + str(artifact_id) )
                else:
                    j = r.json()
                    if args.verbose:
                        print("MODIFY ARTIFACT returned:" + json.dumps(j,indent=4))
                
                    print( "Failed to modify artifact " + str(artifact_id) )
                    return False
            else:
                print( "modified artifact " + str(artifact_id) + " with:\n" + json.dumps(json_modify_bug,indent=4) )

    return True