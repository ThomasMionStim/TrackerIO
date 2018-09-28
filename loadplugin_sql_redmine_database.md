Read a MySQL Redmine database
=============================

This plugin will load issues from an existing Redmine MySQL database

Note that many Redmine issue fields are backed up in a pdf attached to the target tracker new issue.

# 1. How-to

This section describes how to setup the environment to let the plugin be able to load issues from a Redmine MySQL database

The plugin needs:
- [MySQL Connector/Python module][python_mysql] (was tested with v8.0.12)
- [Python/request module][python_request] (was tested with v2.19.1)
- An access to Redmine's MySQL database (was tested with MySQL server 5.5).
- An access to Redmine through HTTP without authentification (this is an option to be set by Redmine administrator) to retrieve attachements (was tested with v1.1.0)

Firstly, you should lock all users to make sure no issue editing is done while you do (and even after you did) the migration.

### 1.1 The easy way

If your Redmine server hosts a MySQL server > v5.5 and can be accessed through http, simply specify the server hosts and MySQL login/password to the script

### 1.2 The other way

If your Redmine server hosts a different SQL environment (like PostgreSQL) or a older version of MySQL or does not have a port opened to let you acess MySQL:

- Dump the Redmine database from the server ('mysqldump --uroot -p <redmine_database_name> -r redmine.sql')
- On your local machine, install [MySQL Server 5.5.60][mysql]
- Configure MySQL's my.ini file to use the same `default-character-set` and `character-set-server` as the server (dunno if that's mandatory, but it's probably safer)
- On your local machine, install [Heidi SQL][heidisql]
- Start MySQL server service and run HeidiSQL, log to "localhost"
- From HeidiSQL, execute redmine.sql with the right encoding (see server's MySQL's my.ini file. Note that HeidiSQL encoding auto-detection may fail and then special characters will be screwed up in your local database)

Now you should specify localhost and local MySQL login/password to the script. Pass Redmine server address to '--sql_redmine_database_url' to make it possible to retrieve attachments and pdf from the server (they are not part of SQL database).

# 2. Known issues, limitations

- Some fields are not imported for real and are just part of the generated pdf to be imported as an attachment
- Archived projects must be restored so that pdf can be downloaded

# 3. TODOs
- Load more fields for real rather than through a pdf export

[python_mysql]: <https://dev.mysql.com/doc/connector-python/en/connector-python-introduction.html>
[python_request]: <http://docs.python-requests.org/en/master/>
[mysql]: <https://downloads.mysql.com/archives/get/file/mysql-5.5.60-winx64.msi>
[heidisql]: <https://www.heidisql.com/download.php>
