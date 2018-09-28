# 1. TrackerIO

### 1.1 Introduction
TrackerIO is a Python module designed to help you migrating issues (bug descriptions) from one tracker tool (Redmine, Tueap, Mantis, Bugzilla...) to another.
Helpful when migrating to a new bug tracker while you don't want to loose your bug history.

Note that the migration is likely to loose some information, so the old tracker database must be maintained or at least archived.

Was tested with Python 3.4.3

### 1.2 TrackerIO principle 

TrackerIO was designed to let you migrate isses from/to any system. It uses a plugin approach for loading/saving, in the middle, it has a issue class storing all information. Of course, each plugin comes with some limitations :-(

##### Load plugin:
Reads a list of issues from the original bug tracker and stores them
##### Save plugin:
Saves the list of issues into the targetted bug tracker

**Right now, it only supports Redmine MySQL database migration to Tuleap**, but it could be extended.

### 1.3 Warning

HE PRODUCT IS PROVIDED “AS IS” WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED. I DO NOT WARRANT THAT THE PRODUCT WILL MEET YOUR REQUIREMENTS OR THAT ITS OPERATION WILL BE UNINTERRUPTED OR ERROR FREE.

**YOU MUST KEEP A BACKUP OF YOUR SOURCE BUG TRACKER DATABASE AND ATTACHMENTS EVEN AFTER YOU CONVERTED THEM.**

You must also adopt a strategy if you are likely to reimport the issues later.
Each loader/saver has limitations: if you migrate issues today, you may loose more information than if you migrate them tomorrow with a most recent version of this tool.
Then, if people modified the imported issues (for follow-up purpose), those changes will be lost if you decide to migrate issues again.
So it is recommanded not to edit imported issues, you should lock them for editing.
For follow-up, you should create new issues (at least for your non-closed issues that are meant to be edited and closed later) for editing. Those new issues should reference the original issue tracker ID (new ID will also change in case of new migration). Note that some tracker propose a copy issue functionnality that could help here.

**If you don't do that, just make sure migration went all right after you did it...and before people starts editing the imported issues.**

# 2. Example:

Read [loadplugin_sql_redmine_database.md][loadplugin_sql_redmine_database] to see how to setup Redmine for loading

Read [saveplugin_tuleap_api.md][saveplugin_tuleap_api] to see how to setup Tuleap for saving

Then run:
> python tracker_io.py --sql_redmine_database_host localhost --sql_redmine_database_login root --sql_redmine_database_password XXXX --sql_redmine_database_databasename test_redmine --sql_redmine_database_url http://my_redmine_server/test_redmine --tuleap_api_host https://trial1.mytuleap.com --tuleap_api_login jpo38 --tuleap_api_password XXXX --tuleap_api_tracker IIII --load_plugin sql_redmine_database --save_plugin tuleap_api

#### General options:

- **--load_plugin**: Specifies the load plugin to be used (here 'sql_redmine_database')
- **--save_plugin**: Specifies the save plugin to be used (here 'tuleap')
- **--dry** can be used to go through the whole process (import, verify tracker compatibility wih imported issues) without actually creating the artifacts
- **-v** can be used for more verbosity

#### Loader options:
- **--sql_redmine_database_host**: specifies the host where MySQL Redmine database can be accessed
- **--sql_redmine_database_login**: specifies the MySQL login
- **--sql_redmine_database_password**: specifies the MySQL password
- **--sql_redmine_database_databasename**: specifies the MySQL database name (containing "issues", "members", "projects"... tables) from which issues are to be loaded
- **--sql_redmine_database_url**: (optional) specifies the http address hosting Redmine where attachments and issue PDF can be downloaded (as they are not part of the database itself)

#### Saver options:
- **--tuleap_api_host**: specifies Tuleap website where artifacts should be saved
- **--tuleap_api_login**: specifies Tuleap login
- **--tuleap_api_password**: specifies Tuleap password
- **--tuleap_api_tracker**: Id of the tracker to create artifacts in (can be found in tracker's URL or tooltip)

Note that if you do not have any Redmine MySQL database available you can use "mockup" for **--load_plugin** and then drop all **--sql_redmine_database_** parameters. This will import in Tuleap two hardcoded issues as a demonstration.

# 3. Available plugins:

To create new plugins, please read [this document][howto_create_new_plugins].

## 3.1 Load plugins:

##### Mockup:
Just creates a few hardcoded issues, for testing purpose
##### Redmine MySQL database:
[Read a MySQL Redmine database][loadplugin_sql_redmine_database]
##### Others (to be implemented):
- [Redmine REST API import][redmine_rest_api]
- Bugzilla import
- Mantis import
- ...

## 3.2 Save plugins:

##### Tuleap through REST API:
[Save bugs in Tuleap using REST API][saveplugin_tuleap_api]
##### Others (to be implemented):
- Tuleap through [XML][tuleap_xml]
- Redmine export
- Bugzilla export
- Mantis export
- ...

# 4. Issue fields loading/saving support:

An issue has many properties that you will want to migrate to the new system. Her is a table of all fields and their suport by existing plugins:

|Property | Type | Count | Must/Should/Nice | Supported by Redmine MySQL database loader | Supported by Tuleap REST API saver |
|------ | ------ | ------ | ------ | ------ | ------ |
| **Title** | string | 1 | Must | <font color=green>YES</font> | <font color=green>YES</font> |
| **Description** | string | 1 | Must | <font color=green>YES</font> | <font color=green>YES</font> |
| **Project name** | string | 1 | Must | <font color=green>YES</font> | <font color=green>YES (as 'original_project')</font> |
| **Tracker name** | string | 1 | Nice | <font color=green>YES</font> | <font color=green>YES (as 'original_tracker')</font> |
| **Author** | user id | 1 | Must | <font color=green>YES</font> | <font color=orange>YES, but as 'originally_submitted_by'</font> (actual author is the one who ran the script) |
| **Submission date** | date | 1 | Must | <font color=orange>YES (1)</font> | <font color=red>NO (not supported by REST API)</font> (2) |
| **Owner** | user id | 1 | Must | <font color=green>YES</font> | <font color=green>YES (as 'originally_owned_by' and 'assigned_to' if login matchs)</font> |
| **Status** | enum{New, Open...} | 1 | Must | <font color=green>YES</font> | <font color=green>YES</font> |
| **Priority** | enum{Critical,High,...} | 1 | Should | <font color=orange>YES</font> | <font color=green>YES</font> |
| **History of changes** | user id + date + change (status, owner...) | N | Nice | <font color=orange>YES (1)</font> | <font color=red>NO (not supported by REST API)</font> (2) |
| **Comments** | user id + date + comment | N | Should | <font color=orange>YES (1)</font> | <font color=red>NO (not supported by REST API)</font> (2) |
| **Attachements** | file | N | Must (specially if the old tracker will be removed for good) | <font color=green>YES</font> | <font color=green>YES</font> |
| **Custom fields** | any | N | Nice | <font color=orange>YES (1)</font> | <font color=red>TODO</font> (2) |
| **Bug original ID** | string | 1 | Must (original ID should be ported, but new issue will have a different ID) | <font color=green>YES</font> | <font color=green>YES (as part of 'original_id')</font> |
| **Linked issues** | issue id | N | Nice | <font color=green>YES</font> | <font color=orange>YES (as hyperlinks in 'import_extra_info', not as real artifact links)</font> |

(1) Not extracted from database but part of part of extracted PDF to be loaded as an attachment

(2) But part of attached PDF when issue was imported from Redmine

# 5. TODOs:
- Extend Bug class to store more information (history of changes, comments...)
- Create more loader/saver (like Tuleap through xml, more powerfull than REST API)

# 6. License
MIT

   [redmine_rest_api]: <http://www.redmine.org/projects/redmine/wiki/Rest_api>
   [tuleap_xml]: <https://tuleap-documentation.readthedocs.io/en/latest/administration-guide/project-export-import.html>
   [loadplugin_sql_redmine_database]: <loadplugin_sql_redmine_database.md>
   [saveplugin_tuleap_api]: <saveplugin_tuleap_api.md>
   [howto_create_new_plugins]: <howto_create_new_plugins.md>