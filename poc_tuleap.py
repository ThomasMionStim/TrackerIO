import requests
import argparse
import json

parser = argparse.ArgumentParser(description="Tuleap import test.")
parser.add_argument("-p", "--password", type=str, help='password')
args = parser.parse_args()

url,login,artifact = "https://codev-tuleap.intra.cea.fr","JP225611",157297

r = requests.post(url + "/api/tokens", json={"username":login, 
                                             "password":args.password}, verify="ca-bundle.crt")

if r.status_code != 201:
    print(r.status_code, r.reason)
    print(r.text[:300] + '...')
    exit(1)

j = r.json()

print("Connected")

user_id = str(j["user_id"])
token = j["token"]
print( "User ID:" + user_id )
print( "Token:" + token )

headersGet = {'X-Auth-UserId': user_id, 'X-Auth-Token': token}
headersPost = {'X-Auth-UserId': user_id, 'X-Auth-Token': token, 'Content-Type': 'application/json', 'Accept': 'application/json'}

#r = requests.get(url + "/api/projects", headers=headersGet, verify="ca-bundle.crt")
#print("GET PROJECTS:" + r.text)
#r = requests.get(url + "/api/artifacts/" + str(artifact), headers=headersGet, verify="ca-bundle.crt")
#print("GET ARTIFACT:" + r.text)

r = requests.get(url + "/api/trackers/" + str(680), headers=headersGet, verify="ca-bundle.crt")
print("GET TRACKERS:" + str(r.json()))

summary_field_id = -1
status_field_id = -1
status_field_new_id = -1

for field in r.json()['fields']:
    if field['name'] == 'summary':
        summary_field_id = field['field_id']
    if field['name'] == 'status_id':
        status_field_id = field['field_id']
        for value in field['values']:
            if value['label'] == 'New':
                status_field_new_id = value['id']

print( "Summary field ID is " + str(summary_field_id) )
print( "Status field ID is " + str(status_field_id) )
print( "Status field New value's ID is " + str(status_field_new_id) )

# status field_id is 20641 and "New" id is 19208
# summary field_id is 20630
# Create a new artifact with status "New"
r = requests.post(url + "/api/artifacts", headers=headersPost, json=
{
  "tracker": {
    "id": 680
             },
  "values": [
    {
      "field_id": status_field_id,
      "bind_value_ids": [status_field_new_id]
    },
    {
      "field_id": summary_field_id,
      "value": "Created by Jean"
    }
  ]
}, verify="ca-bundle.crt")

print("CREATE ARTIFACT:" + r.text)

print( "Created artifact " + str(r.json()['id']))


