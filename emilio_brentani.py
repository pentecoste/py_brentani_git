from pyrogram import Client, filters
import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import time
import datetime
import json

GROUP_ID = -730750219

# Gestisce i warning per le scadenze degli alimenti
async def warning():
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        keys = []
        for key, exp_time in data["warnings"].items():
            if exp_time < time.time():
                keys.append(key)
                await app.send_message(GROUP_ID, "Attenti! " + data["elements"][key]["name"] + " sta per scadere!")
        for key in keys:
            del data["warnings"][key]
        with open('data.json', 'w') as outfile:
            try:
                json.dump(data, outfile, sort_keys=True, indent=4)
            except Exception as e:
                print("Unable to write JSON file data.json\n\n" + str(e))
                return

#Funzione per tenere una log della contabilità per prevenire errori
async def log_handler():
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        with open("log.txt", "a") as outfile:
            ts = datetime.datetime.fromtimestamp(time.time()).strftime("[%b %d %Y %H:%M:%S]")
            outfile.write(ts + " " + str(data["credits"]) + "\n")
            



app = Client("Emilio Brentani", bot_token = config.API_TOKEN)

scheduler = AsyncIOScheduler()
scheduler.add_job(warning, "interval", seconds=20)
scheduler.add_job(log_handler, "interval", seconds=43200)

scheduler.start()
app.run()

