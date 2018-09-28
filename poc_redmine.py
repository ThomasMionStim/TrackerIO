import mysql.connector
from mysql.connector import errorcode

database = 'testredmine'
verbose = False

def getProjects( cnx ):
    projects_cursor = cnx.cursor()
    projects_cursor.execute("SELECT id, name FROM projects")
    res = dict()
    for (id,name) in projects_cursor:
        if verbose:
            print( "project id=" + str(id) + " " + str(type(id)) )
            print( "project name=" + str(name) + " " + str(type(name)) )
        res[id] = name
    projects_cursor.close()
    return res

try:
    cnx = mysql.connector.connect(user='root', password='biomed',
                                  host='127.0.0.1',
                                  database=database)
except mysql.connector.Error as err:
    
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    elif err.errno == errorcode.ER_HANDSHAKE_ERROR:
        print(err)
        print("Not MySQL version must be 8.0, 5.7, 5.6, and 5.5")
    else:
        print(err)

else:

    for project_id, project_name in getProjects(cnx).items():
        print("Project: " + str(project_name))

        issues_cursor = cnx.cursor()
        issues_cursor.execute("SELECT id, project_id, subject FROM issues WHERE project_id=" + str(project_id))
        for (id,project_id,subject) in issues_cursor:
            if verbose:
                print( "issue id=" + str(id) + " " + str(type(id)) )
                print( "issue subject=" + str(subject) + " " + str(type(subject)) )
            print("    Issue #" + str(id) + ": " + subject)
        issues_cursor.close()

    cnx.close()