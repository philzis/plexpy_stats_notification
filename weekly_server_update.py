import requests
import json
import sys


PLEXPY_URL = ''
PLEXPY_APIKEY = ''
AGENT_ID = 13 #pushbullet = 7; telegram = 13
SUBJECT_TEXT = "Weekly Update!!!"
SERVER_SIZE = '18 TB'

#define the function for sending the notification
def send_notification(BODY_TEXT):
    # Format notification text
    try:
        subject = SUBJECT_TEXT
        body = BODY_TEXT
    except LookupError as e:
        sys.stderr.write("Unable to substitute '{0}' in the notification subject or body".format(e))
        return None
    # Send the notification through PlexPy
    payload = {'apikey': PLEXPY_APIKEY,
               'cmd': 'notify',
               'agent_id': AGENT_ID,
               'subject': subject,
               'body': body}

    try:
        r = requests.post(PLEXPY_URL.rstrip('/') + '/api/v2', params=payload)
        response = r.json()

        if response['response']['result'] == 'success':
            sys.stdout.write("Successfully sent PlexPy notification.")
        else:
            raise Exception(response['response']['message'])
    except Exception as e:
        sys.stderr.write("PlexPy API 'notify' request failed: {0}.".format(e))
        return None

###############################
# 1 Get Home Stats
###############################

#generate URL for API call for getting home statistics
payload = {'apikey': PLEXPY_APIKEY,
           'cmd': 'get_home_stats',
           'stats_type': 1,
            'time_range': '7'}

r = requests.get(PLEXPY_URL.rstrip('/') + '/api/v2', params=payload)

#put all JSON data in a variable
response = r.json()

#search for the "top_users" within the json data
data = response["response"]["data"][7]["rows"]

#create a new dict for USER:DURATION
user_duration_dict = {}

#create a new list, in which the finished texts for the notification will be stored
notify_lst = []

#write inside the new dictonary
for value in data:
     a = ((value["total_duration"])/60)/60
     b = str(a)
     c = b[0:4]
     user_duration_dict[value["friendly_name"]] = c
     
#put all data from users into a list
for key, value in user_duration_dict.items():
     notify_lst += [u"{}: {} h \n".format(key, user_duration_dict[key])]

#put the lists into a string, so it can be sent via non-html notifications
notify_lst_str = ''.join(notify_lst)

###############################
# 2 Get  all users on the server
###############################

#generate URL for API call for getting all users from server
payload2 = {'apikey': PLEXPY_APIKEY,
           'cmd': 'get_user_names'}

r2 = requests.get(PLEXPY_URL.rstrip('/') + '/api/v2', params=payload2)

#write that data into a variable
response_user_names = r2.json()

#get the to where the usernames are
data_user_names = response_user_names["response"]["data"]

#create a new list with all user names

user_names_lst = []

#write the names in a list

for value in data_user_names:
     user_names_lst.append(value["friendly_name"])

#delete the user "local"
del user_names_lst[0]

#get the the names that are on the server, but have not watched something this week
non_users_lst = set(user_names_lst).difference(user_duration_dict)

#put the lists into a string, so it can be sent via non-html notifications
non_users_str = ' and '.join(non_users_lst)

###############################
#Get server statistics
###############################

#generate URL for API call for getting all users from server
payload3 = {'apikey': PLEXPY_APIKEY,
           'cmd': 'get_libraries'}

r3 = requests.get(PLEXPY_URL.rstrip('/') + '/api/v2', params=payload3)

#write that data into a variable
response_server_stats = r3.json()

#get the to where the counbt of media is
data_server_stats = response_server_stats["response"]["data"]


#create a new list with all counts

library_count_dict = {}
library_childcount_dict = {}

#write the count in that dict

for value in data_server_stats:
     library_count_dict[value["section_name"]] = value["count"]

#write the child count in  dict

episode_count = response_server_stats["response"]["data"][3]["child_count"]

#put the list into the BODY TEXT of the notification
BODY_TEXT = '\n<b>Plex Server Statistics:</b> \n - Movies: ' + library_count_dict['Filme'] + '\n - TV-Shows: ' + library_count_dict['TV-Serien'] + '\n - Episodes: ' + episode_count + '\n - Server Capacity: ' + SERVER_SIZE + '\n \n<b>User Activity Top 10:</b> \n' + notify_lst_str + ' \n \nThis week we missed: <i>' + non_users_str + '</i>.\nTime to come back!'

#print(BODY_TEXT)
#send the notification
send_notification(BODY_TEXT)




        





