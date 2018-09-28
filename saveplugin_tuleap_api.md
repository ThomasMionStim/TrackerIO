
Save bugs in Tuleap using REST API
=========================

This plugin will save issues to an existing Tuleap tracker using [Tuleap REST API][tuleap_rest_api]

# 1. How-to

This section describes how to setup the environment to let the plugin be able to save issues to a Tuleap tracker

The plugin needs:
- [Python/request module][python_request] (was tested with v2.19.1)
- An access to Tuleap tracker

The plugin will check if available fields and field values are compatible for the import.

#### Create the tracker

The tracker requires some fields:

| Target field name | Required field  | Comment |
| ------ | ------ | ------ |
| **summary**  | YES | Allowed size should be > 300 |
| **details**  | YES |   |
| **status_id**  | YES | Must allow new artifact to be created with other status than "New"  |
| **severity**  | YES |   |
| **originally_submitted_by**  | YES | Artifact author will be the one wo ran TrackerIO, real issue owner will be saved here if available |
| **originally_owned_by**  | YES | Original issue owner may not be a Tuleap user, then the artifact will be assigned to none but original issue owner will be saved here |
| **assigned_to**  | YES | May stored original issue owner if it has the same name in Tuleap |
| **original_id**  | YES | Stores original tracker's issue identifier |
| **original_tracker**  | NO | Stores original tracker's name |
| **import_extra_info**  | YES | Stores any information that could not be stored anywhere else (issue relations and any information to be stored in a missing non-required field) |
| **original_project**  | YES | Stores old tracker's project name |

You can either create them by hand or use provided Tracker_Tuleap_imported_by_trackerIO.xml file to create the tracker in Tuleap with the appropriate fields available.

#### Identify the tracker

Tracker ID will be passed as a script parameter. To identify your tracker ID, either check the browser URL while using the tracker (http://mytuleap/plugins/tracker/?tracker=XXXX), either check the tracker tooltip from the trackers tab.

#### Make it possible to later re-import artifacts with a newer version of the script

After the script was run once, you must not modify the imported artifacts (alse changes will be lost if you re-import artifacts later with a newer version of the script).

Unfortunately, there is currently no way to lock artifacts for editing (see https://tuleap.net/plugins/tracker/?aid=12332).

You should copy them to a different tracker for editing, to do so:
- Export tracker's description as xml
- Create a new alive tracker
- Export imported "open" artifacts as csv
- Open the csv and delete the "aid" column
- Import the csv to the "alive" tracker

# 2. Known issues, limitations
- Attachments bigger than 1Mo can't be imported.

# 3. TODOs
- Possibly make some target fields optional but then save issue attribute in 'import_extra_info' field
- Link artifacts for real (not only as text information in 'import_extra_info' field)
- Support import of files bigger than 1Mo (needs the file to be posted in chunks)

[python_request]: <http://docs.python-requests.org/en/master/>
[tuleap_rest_api]: <https://tuleap-documentation.readthedocs.io/en/latest/user-guide/rest.html>