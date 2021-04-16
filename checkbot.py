import discord
import requests
import json
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from time import time
import threading

threadreturnlist = []

file = open("info.json", "r")
info = json.load(file)
realm = info[0]
guild = info[1]
discordToken = info[2]
bnetToken=[info[3],info[4]]



class analysisthread(threading.Thread):
    def __init__(self, member, token):
        threading.Thread.__init__(self)
        self.token = token
        self.member = member

    def run(self):
        threadLock.acquire()
        try:
            char = requests.get(self.member['character']['key']['href']+"&locale=en_US&access_token=" +
                                token['access_token'], headers={"Authorization": "Bearer "+token['access_token']}).json()
            chartime = char["last_login_timestamp"]
        except:
            threadLock.release()
        else:
            howlongago = abs(chartime-round(time() * 1000))/1000
            threadreturnlist.append([char["name"], howlongago])
            threadLock.release()


threadLock = threading.Lock()

try:
    tokenRequest = requests.post('https://eu.battle.net/oauth/token', auth=HTTPBasicAuth(
        bnetToken[0], bnetToken[1]), data={"grant_type": "client_credentials"})
    tokenRequest.raise_for_status()
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')  # Python 3.6
except Exception as err:
    print(f'Other error occurred: {err}')  # Python 3.6
else:
    print('Success! Token has been retrieved.')
token = tokenRequest.json()


client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user} '.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!online'):
        answer = requests.get("https://eu.api.blizzard.com/data/wow/guild/"+realm+"/"+guild+"/roster?namespace=profile-eu&locale=en_US&access_token=" +
                              token['access_token'], headers={"Authorization": "Bearer "+token['access_token']}).json()
        print(answer["members"])
        returnmsg = "Current online members : "
        threads = []
        for member in answer["members"]:
            thread = analysisthread(member, token)
            thread.start()
            threads.append(thread)
        for t in threads:
            t.join()
        for i in threadreturnlist:
            print(i[0], i[1])
            howlongago = i[1]
            if howlongago <= 36000:
                returnmsg += i[0]+" has been seen: " + \
                    str(round(howlongago/60))+" minutes ago , "

        await message.channel.send(returnmsg)

client.run(discordToken)
