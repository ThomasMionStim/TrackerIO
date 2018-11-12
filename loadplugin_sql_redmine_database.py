# coding: utf8

import argparse
import getpass
from tracker_io_common import Bug, Attachment, child_of_relation_type, parent_of_relation_type, sizeof_fmt

def addArguments( parser ):
    parser.add_argument("--sql_redmine_database_host", metavar="host", type=str, help='MySQL host')
    parser.add_argument("--sql_redmine_database_login", metavar="username", type=str, help='MySQL login')
    parser.add_argument("--sql_redmine_database_password", metavar="password", type=str, help='MySQL password (optional)')
    parser.add_argument("--sql_redmine_database_databasename", metavar="database", type=str, help='MySQL database name')
    parser.add_argument("--sql_redmine_database_url", metavar="url", type=str, help='Redmine URL to doanload attachments from')

def checkArguments( args ):

    if args.sql_redmine_database_host == None or args.sql_redmine_database_host == "":
        print("No MySQL host specified")
        return False
    if args.sql_redmine_database_login == None or args.sql_redmine_database_login == "":
        print("No MySQL login specified")
        return False
    if args.sql_redmine_database_databasename == None or args.sql_redmine_database_databasename == "":
        print("No MySQL database specified")
        return False

    if args.sql_redmine_database_password == None or args.sql_redmine_database_password == "":
        args.sql_redmine_database_password = getpass.getpass( "Please enter Redmine password: ")

    # sql_redmine_database_url is optional 

    print( "Will load bugs from " + args.sql_redmine_database_host )

    return True

class RedmineProjectInfo:
    """A Redmine project description"""
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.bugs = []

def getProjects( cnx, verbose ):
    projects_cursor = cnx.cursor()
    projects_cursor.execute("SELECT id, name FROM projects")
    res = []
    for (id,name) in projects_cursor:
        if verbose:
            print( "project id=" + str(id) + " " + str(type(id)) )
            print( "project name=" + str(name) + " " + str(type(name)) )
        res.append( RedmineProjectInfo( name, id ) )
    projects_cursor.close()
    return res

def getUsersMap( cnx, verbose ):
    users_cursor = cnx.cursor()
    users_cursor.execute("SELECT id, login FROM users")
    res = dict()
    for (id,login) in users_cursor:
        if verbose:
            print( "user id=" + str(id) + " " + str(type(id)) )
            print( "user login=" + str(login) + " " + str(type(login)) )
        res[id] = login
    users_cursor.close()
    return res

def getStatusMap( cnx, verbose ):
    status_cursor = cnx.cursor()
    status_cursor.execute("SELECT id, name FROM issue_statuses")
    res = dict()
    for (id,name) in status_cursor:
        if verbose:
            print( "status id=" + str(id) + " " + str(type(id)) )
            print( "status name=" + str(name) + " " + str(type(name)) )
        res[id] = name
    status_cursor.close()
    return res

def getTrackersMap( cnx, verbose ):
    trackers_cursor = cnx.cursor()
    trackers_cursor.execute("SELECT id, name FROM trackers")
    res = dict()
    for (id,name) in trackers_cursor:
        if verbose:
            print( "status id=" + str(id) + " " + str(type(id)) )
            print( "status name=" + str(name) + " " + str(type(name)) )
        res[id] = name
    trackers_cursor.close()
    return res

def getPriorityMap( cnx, verbose ):
    priority_cursor = cnx.cursor()
    priority_cursor.execute("SELECT id, name, type FROM enumerations")
    res = dict()
    for (id,name,type) in priority_cursor:
        #if verbose:
        #    print( "priority id=" + str(id) + " " + str(type(id)) )
        #    print( "priority name=" + str(name) + " " + str(type(name)) )
        #    print( "priority type=" + str(type) + " " + str(type(type)) )
        if type == "IssuePriority":
            res[id] = name
    priority_cursor.close()
    return res
    
def getAttachementsMap( cnx, verbose ):
    attachment_cursor = cnx.cursor()
    attachment_cursor.execute("SELECT id, container_id, filename, content_type FROM attachments WHERE container_type='Issue'")
    res = dict()
    for (id, container_id, filename, content_type) in attachment_cursor:
        if verbose:
            print( "attachment id=" + str(id) + " " + str(type(id)) )
            print( "attachment container_id=" + str(container_id) + " " + str(type(container_id)) )
            print( "attachment filename=" + str(filename) + " " + str(type(filename)) )
            print( "attachment content_type=" + str(content_type) + " " + str(type(content_type)) )
        if not container_id in res:
            res[container_id] = []
        res[container_id].append([id,filename,content_type])
    attachment_cursor.close()
    return res

def getIssueRelationsMap( cnx, verbose ):
    relations_cursor = cnx.cursor()
    relations_cursor.execute("SELECT id, issue_from_id, issue_to_id, relation_type FROM issue_relations")
    res = []
    for (id, issue_from_id, issue_to_id, relation_type) in relations_cursor:
        if verbose:
            print( "relation id=" + str(id) + " " + str(type(id)) )
            print( "relation issue_from_id=" + str(issue_from_id) + " " + str(type(issue_from_id)) )
            print( "relation issue_to_id=" + str(issue_to_id) + " " + str(type(issue_to_id)) )
            print( "relation relation_type=" + str(relation_type) + " " + str(type(relation_type)) )
        res.append([issue_from_id,issue_to_id,relation_type])
    relations_cursor.close()
    return res
    
def GetIDAsText( id ):
    return "Redmine#" + str(id)

def loadBugs( args ):

    import mysql.connector
    from mysql.connector import errorcode
    import urllib.request
    import requests

    bugs_to_import = []
        
    try:
        cnx = mysql.connector.connect(user=args.sql_redmine_database_login, 
                                      password=args.sql_redmine_database_password,
                                      host=args.sql_redmine_database_host,
                                      database=args.sql_redmine_database_databasename)

    except mysql.connector.Error as err:

        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        elif err.errno == errorcode.ER_HANDSHAKE_ERROR:
            print(str(err))
            print("Note MySQL version must be 8.0, 5.7, 5.6, and 5.5")
        else:
            print(str(err))

    else:

        projects = getProjects(cnx,args.verbose)
        users = getUsersMap(cnx,args.verbose)
        statuses = getStatusMap(cnx,args.verbose)
        trackers = getTrackersMap(cnx,args.verbose)
        priorities = getPriorityMap(cnx,args.verbose)
        attachments = getAttachementsMap(cnx,args.verbose)
        relations = getIssueRelationsMap(cnx,args.verbose)

        if args.verbose:
            print( "Redmine projects: " + str(projects) )
            print( "Redmine users: " + str(users) )
            print( "Redmine statuses: " + str(statuses) )
            print( "Redmine trackers: " + str(trackers) )
            print( "Redmine priorities: " + str(priorities) )
            print( "Redmine attachments: " + str(attachments) )

        bug_id_to_databaseid = dict()
        for project_info in projects:
            
            # Quickly get list of bugs
            issues_cursor = cnx.cursor()
            issues_cursor.execute("SELECT id, project_id, tracker_id, assigned_to_id, status_id, priority_id, author_id, subject, description, parent_id, created_on FROM issues WHERE project_id=" + str(project_info.id))
            for (id,project_id,tracker_id,assigned_to_id,status_id,priority_id,author_id,subject,description,parent_id,created_on) in issues_cursor:
                if args.verbose:
                    print( "issue id=" + str(id) + " " + str(type(id)) )
                    print( "issue project_id=" + str(project_id) + " " + str(type(project_id)) )
                    print( "issue tracker_id=" + str(tracker_id) + " " + str(type(tracker_id)) )
                    print( "issue subject=" + str(subject) + " " + str(type(subject)) )
                    print( "issue author_id=" + str(author_id) + " " + str(type(author_id)) )
                    print( "issue created_on=" + str(created_on) + " " + str(type(created_on)) )
                    print( "issue assigned_to_id=" + str(assigned_to_id) + " " + str(type(assigned_to_id)) )
                    print( "issue status_id=" + str(status_id) + " " + str(type(status_id)) )
                    print( "issue priority_id=" + str(priority_id) + " " + str(type(priority_id)) )
                    print( "issue description=" + str(description) + " " + str(type(description)) )

                bug = Bug()
                
                bug.summary = subject
                bug.project = "Redmine \"" + project_info.name + "\""
                bug.description = description
                bug.old_id = GetIDAsText(id)
                bug_id_to_databaseid[bug.old_id] = id
                if status_id != None and status_id in statuses:
                    bug.setStatus( statuses[status_id] )
                if tracker_id != None and tracker_id in trackers:
                    bug.tracker = trackers[tracker_id]
                if priority_id != None and priority_id in priorities:
                    bug.setSeverityFromText( priorities[priority_id] )
                if author_id != None and author_id in users:
                    bug.author = users[author_id]
                if created_on != None and author_id in users:
                    bug.submit_date = created_on
                if assigned_to_id != None and assigned_to_id in users:
                    bug.owner = users[assigned_to_id]
                if parent_id != None:
                    bug.related_ids[child_of_relation_type] = [GetIDAsText(parent_id)]

                for (issue_from_id, issue_to_id, relation_type) in relations:
                    if issue_from_id == id:
                        if not relation_type in bug.related_ids:
                            bug.related_ids[relation_type] = []
                        bug.related_ids[relation_type].append( GetIDAsText(issue_to_id) )
                    if issue_to_id == id:
                        relation = "reverse_" + relation_type
                        if not relation in bug.related_ids:
                            bug.related_ids[relation] = []
                        bug.related_ids[relation].append( GetIDAsText(issue_from_id) )

                project_info.bugs.append( bug )

            issues_cursor.close()

        for project in projects:
            # Update parent_of_field
            for bug in project.bugs:
                if child_of_relation_type in bug.related_ids:
                    for parent_id in bug.related_ids[child_of_relation_type]:
                        # find parent and set relation info:
                        found = False
                        for i in range(len(projects)):
                            for j in range(len(projects[i].bugs)):
                                if projects[i].bugs[j].old_id == parent_id:
                                    assert not found
                                    if not parent_of_relation_type in projects[i].bugs[j].related_ids:
                                        projects[i].bugs[j].related_ids[parent_of_relation_type] = []
                                    projects[i].bugs[j].related_ids[parent_of_relation_type].append(bug.old_id)
                                    if args.verbose:
                                        print( projects[i].bugs[j].project + ": Added parent relation from " + projects[i].bugs[j].old_id + " to " + bug.old_id )
                                    found = True
                        assert found

        choiceStr = "\nPlease select a project to import:\n"
        index = 1
        total_bugs_count = 0
        choiceStr += "0: Cancel\n"
        for project_info in projects:
            choiceStr += str(index) + ": Project: " + project_info.name + " (id=" + str(project_info.id) + ") with " + str(len(project_info.bugs)) + " Redmine issue(s)\n"
            total_bugs_count += len(project_info.bugs)
            index += 1
        choiceStr += str(index) + ": All projects (" + str(total_bugs_count) + ") Redmine issue(s)\n"

        while ( True ):
            choice = input(choiceStr)
            try:
                choice_index = int(choice)
                if choice_index == 0:
                    break
                elif choice_index == index:
                    for project_info in projects:
                        for bug in project_info.bugs:
                            bugs_to_import.append( bug )
                    break
                elif choice_index >= 1 and choice_index < index:
                    bugs_to_import = projects[choice_index-1].bugs[:]
                    break
            except ValueError:
                print("Invalid choice...!")
                continue

        cnx.close()

        for i in range(len(bugs_to_import)):

            if args.sql_redmine_database_url != None and args.sql_redmine_database_url != "" and len(bugs_to_import) != 0:

                redmine_bug_id = bug_id_to_databaseid[bugs_to_import[i].old_id]

                # generate PDF to import all bug history and comments that it would be hard to import in target trackers like Tuleap using REST API
                pdfSourceName = str(redmine_bug_id) + ".pdf"
                pdfTargetName = "redmine_history_of_" + pdfSourceName
                print("Generating " + pdfTargetName)
                url = args.sql_redmine_database_url + "/issues/" + pdfSourceName
                r = requests.get(url)
                if r.status_code != 200:
                    if args.verbose:
                        print("PDF download error " + str(r.status_code) + ": " + str(r.content))
                    print("Unable to download " + url)
                    exit(1)
                
                # Expecting content to be b'%PDF
                if str(r.content).find("%PDF") != 2:
                    if args.verbose:
                        print("PDF content:" + str(r.content))
                    print("Invalid PDF " + url)
                    exit(1) 
                else:
                    print( "Done, file size is " + sizeof_fmt( len(r.content) ) )

                bugs_to_import[i].attachments[pdfTargetName] = Attachment( r.content, "application/pdf" )

                # download orginal attachments:
                if redmine_bug_id in attachments:
                    for (file_id,filename,content_type) in attachments[redmine_bug_id]:
                        # generate PDF to import all bug history and comments that it would be hard to import in target trackers like Tuleap using REST API
                        targetName = "from_redmine_" + filename
                        print("Downloading " + filename + " for " + bugs_to_import[i].old_id )
                        url = args.sql_redmine_database_url + "/attachments/download/" + str(file_id) + "/" + filename
                        r = requests.get(url)
                        if r.status_code != 200:
                            if args.verbose:
                                print("Attachment download error " + str(r.status_code) + ": " + str(r.content))
                            print("Unable to download " + filename)
                            exit(1) 
                        else:
                            print( "Done, file size is " + sizeof_fmt( len(r.content) ) )
                        bugs_to_import[i].attachments[targetName] = Attachment( r.content, content_type )
                        
    return bugs_to_import