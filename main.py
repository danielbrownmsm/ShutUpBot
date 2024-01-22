import discord, time, re

#TODO
# - clean up the code
# - find ways to optimize it (don't care for performance, but do care for battery and stuff)
# - 

# might need to account for @person#1234 shut up
# if you're on desktop then it adds a '!' to the @ but if you're on mobile it doesn't
expression = "((?<=shut up <@!)\d+)|((?<=shut up <@)\d+)"

SHUTUP_TIME = 10 # how long someone will be shut-up, in seconds (I think)
SHUTUP_COOLDOWN = 20 #24 * 60 * 60 # a day (but probably want to lower that idk)
FILE_WRITE_INTERVAL = 60 # write every minute (should be enough for most cases, not like we're gonna go down randomly)

class ShutUpBotClient(discord.Client):
    async def on_ready(self):
        print('Connected!')
        print('Username: {0.name}\nID: {0.id}'.format(self.user))
        print(time.strftime("%I:%M:%S"))

        self.people = {}
        self.leaderboard = []
        self.lastFileWriteTime = 0
        try:
            with open("people.txt", "r") as f:
                people = f.readlines()
                for person in people:
                    name = person[:person.index(":")].strip() # the name is the bit before the ':'
                    details = person[person.index(":")+1:].strip().split(",")

                    self.people[name] = {
                            "lastTimeWasShutUp":float(details[0]),
                            "lastTimeUsedShutUp":float(details[1]),
                            "numberUsedShutUp":int(details[2]),
                            "numberBeenShutUp":int(details[3]),
                            "hasBeenWarned":False
                        }
            print("processed persistent file data")
        except Exception as e:
            print("exception occured")
            print(e)

    async def on_message(self, message):
        #TODO also make sure we don't process messages from ourself

        if message.author.name not in self.people:
            self.people[message.author.name] = {
                "lastTimeWasShutUp":0,
                "lastTimeUsedShutUp":0,
                "numberUsedShutUp":0,
                "numberBeenShutUp":0,
                "hasBeenWarned":False
            }
            print("added " + message.author.name)
        
        person = self.people[message.author.name]
        match = re.search(expression, message.content.lower())
        #print(message.content)
        if (time.time() - person["lastTimeWasShutUp"]) < SHUTUP_TIME:
            print("deleted message")
            await message.delete()
            if not person["hasBeenWarned"]:
                #await message.channel.send(message.author.name + " probably said something important but you can't hear it because they've been shut up")
                person["hasBeenWarned"] = True
                print("warned " + message.author.name)
        
        elif message.content.startswith("=leaderboard"):
            print("recieved leaderboard commanad")
            self.leaderboard = []
            for name, details in self.people.items():
                self.leaderboard.append((name, details["numberUsedShutUp"]))
            self.leaderboard = sorted(self.leaderboard, reverse=True, key=lambda d: d[1])
            print(self.leaderboard)
            leaderboard = ""
            for index, tup in enumerate(self.leaderboard):
                if tup[1] > 0:
                    leaderboard += str(index+1) + ". " + tup[0] + ": " + str(tup[1])
            await message.channel.send(leaderboard)
            
        elif match is not None:
            #print("==got a match==")
            victim = await self.fetch_user(int(match.group()))
            victim = victim.name
            print(victim)

            if victim not in self.people:
                self.people[victim] = {
                    "lastTimeWasShutUp":0,
                    "lastTimeUsedShutUp":0,
                    "numberUsedShutUp":0,
                    "numberBeenShutUp":0,
                    "hasBeenWarned":False
                }

            #we've got ourselves a shut up
            if (time.time() - person["lastTimeUsedShutUp"]) > SHUTUP_COOLDOWN:
                print(message.author.name + " shut up " + victim)
                self.people[victim]["lastTimeWasShutUp"] = time.time()
                self.people[victim]["numberBeenShutUp"] += 1

                person["lastTimeUsedShutUp"] = time.time()
                person["numberUsedShutUp"] += 1
                await message.channel.send(message.author.name + " shut up " + victim)
            else:
                # make a hasBeenWarned for cooldown too?
                print(message.author.name + " still on cooldown")
                #await message.channel.send(message.author.name + " is still on cooldown")
        
        if (time.time() - self.lastFileWriteTime) > FILE_WRITE_INTERVAL:
            with open("people.txt", "w") as f:
                for name, details in self.people.items():
                    f.write(name + ":"
                            + str(details["lastTimeWasShutUp"]) + ","
                            + str(details["lastTimeUsedShutUp"]) + ","
                            + str(details["numberUsedShutUp"]) + ","
                            + str(details["numberBeenShutUp"]) + "\n")
            self.lastFileWriteTime = time.time()
            print("wrote persistent data")

client = ShutUpBotClient()
client.run("")
#might want to regen this at some point later like actually tho