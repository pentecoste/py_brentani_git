import config
import json
from pyrogram import filters,Client
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import BadRequest, FloodWait

# Gestisce il comando /start
@Client.on_message(filters.command(["start"]))
async def start(client, message):
    try:
        await client.send_message(message.chat.id, "Ciao, sono un inetto!", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Liste",callback_data="menu_lista")],[InlineKeyboardButton("Cose da fare",callback_data="todo")],[InlineKeyboardButton("Piatti",callback_data="piatti")],[InlineKeyboardButton("Contabilità",callback_data="menu_contabilita")]]))
    except FloodWait:
        return

# Gestisce il callback start
@Client.on_callback_query(filters.regex("start"))
async def start_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    try:
        await client.edit_message_text(chat_id, message_id, "Ciao, sono un inetto!", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Liste",callback_data="menu_lista")],[InlineKeyboardButton("Cose da fare",callback_data="todo")],[InlineKeyboardButton("Piatti",callback_data="piatti")],[InlineKeyboardButton("Contabilità",callback_data="menu_contabilita")]]))
    except (BadRequest, FloodWait) as e:
        return

# Gestisce il comando /help
@Client.on_message(filters.command(["help"]))
async def help (client, message):
    try:
        await client.send_message(message.chat.id, config.help_message)
    except FloodWait:
        return

# Gestisce il callback per il menu delle liste
@Client.on_callback_query(filters.regex("menu_lista"))
async def menu_lista(client, callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        buttons = [[InlineKeyboardButton("Mia & Comune", callback_data = "lista -1")],[InlineKeyboardButton("Comune",callback_data = "lista 0")]]
        for id_ in data["users"]:
            buttons.append([InlineKeyboardButton(data["users"][id_], callback_data = "lista " + id_)])
        buttons.append([InlineKeyboardButton("Mia & Comune (Da fare)", callback_data = "lst_todo -1")])
        buttons.append([InlineKeyboardButton("Comune (Da fare)",callback_data = "lst_todo 0")])
        for id_ in data["users"]:
            buttons.append([InlineKeyboardButton(data["users"][id_] + " (Da fare)", callback_data = "lst_todo " + id_)])
        buttons.append([InlineKeyboardButton("\U0001F519 Back", callback_data = "start")])
        try:
            await client.edit_message_text(chat_id, message_id, "Quale lista della spesa vuoi vedere?", reply_markup = InlineKeyboardMarkup(buttons))
        except (BadRequest, FloodWait) as e:
            return

# Gestisce il callback per il menu della contabilità
@Client.on_callback_query(filters.regex("menu_contabilita"))
async def menu_contabilita(client, callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        buttons = []
        for id_ in data["users"]:
            buttons.append([InlineKeyboardButton(data["users"][id_], callback_data = "contabilita " + id_)])
        buttons.append([InlineKeyboardButton("\U0001F519 Back", callback_data = "start")])
    try:
        await client.edit_message_text(chat_id, callback_query.message.message_id, "Quale contibilità vuoi controllare?", reply_markup = InlineKeyboardMarkup(buttons))
    except (BadRequest, FloodWait) as e:
        return

# Gestisce il callback per le liste di elementi
@Client.on_callback_query(filters.regex("lista"))
async def lista(client, callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        if not str(user_id) in data["users"]:
            try:
                await client.edit_message_text(chat_id, message_id, "Non sei registrato, pertanto non puoi accedere alla lista della spesa", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("\U0001F519 Back", callback_data = "menu_lista")]]))
            except FloodWait:
                return
            return
        callback_data = callback_query.data.split(" ")
        search_id = int(callback_data[1])
        if len(callback_data) > 2:
            toggle_id = callback_data[2]
            was_done = data["elements"][toggle_id]["is_done"]
            data["elements"][toggle_id]["is_done"] = not data["elements"][toggle_id]["is_done"]
            toggled_user = data["elements"][toggle_id]["user_id"]
            price = data["elements"][toggle_id]["price"]
            name = data["elements"][toggle_id]["name"]
            quantity = data["elements"][toggle_id]["quantity"]
            if not was_done:    
                if not (str(user_id) in data["credits"] and str(toggled_user) in data["credits"][str(user_id)]):
                    data["credits"][str(user_id)][str(toggled_user)] = {"value":0.0}
                data["credits"][str(user_id)][str(toggled_user)]["value"] += price
                if not toggled_user:
                    for id_ in data["users"]:
                        if int(id_) != user_id:
                            try:
                                await client.send_message(int(id_), data["users"][str(user_id)] + " gà crompà el " + name + " x" + str(quantity) + " (Comune). Ringrassia!") 
                            except FloodWait as e:
                                return
                elif toggled_user != user_id:
                    try:
                        await client.send_message(toggled_user, data["users"][str(user_id)] + " gà crompà el to " + name + " x" + str(quantity) + ". Ringrassia!") 
                    except FloodWait as e:
                        return
            with open('data.json', 'w') as outfile:
                try:
                    json.dump(data, outfile, sort_keys=True, indent=4)
                except Exception as e:
                    print("Unable to write JSON file data.json\n\n" + str(e))
                    return
        elements_filtered = []
        last_index = 0
        for e in sorted(data["elements"].values(), key = lambda k: k["name"]):
            if search_id == -1:
                if e["user_id"] == user_id or not e["user_id"]:
                    if e["user_id"]:
                        elements_filtered.append(e)
                    else:
                        elements_filtered.insert(last_index, e)
                        last_index += 1
            elif search_id == user_id:
                if e["user_id"] == search_id:
                    elements_filtered.append(e)
            else:
                if e["user_id"] == search_id and (not e["is_private"] or not search_id):
                    elements_filtered.append(e)
        elements_processed = []
        for e in elements_filtered:
            cb_data = "lista " + str(search_id)+ " " + [k for k, v in data["elements"].items() if v == e][0]
            elements_processed.append([InlineKeyboardButton(("(C)    " if not e["user_id"] else "") + ("\U0001F7E2" if e["is_done"] else "\U0001F534") + " " + e["name"] + " x" + str(e["quantity"]) + (" \U0001F7E2 " if e["is_done"] else " \U0001F534") + "    € " + str(e["price"]), callback_data = cb_data)])
        elements_processed.append([InlineKeyboardButton("\U0001F519 Back", callback_data = "menu_lista")])
        username = ""
        if not search_id:
            username = " in comune"
        elif search_id == -1:
            username = " di " + data["users"][str(user_id)] + " e in comune"
        else:
            username = " di " + data["users"][str(search_id)]
        try:
            await client.edit_message_text(chat_id, message_id, "\U00002B07 **LISTA" + username.upper() + "** \U00002B07", reply_markup = InlineKeyboardMarkup(elements_processed))
        except (BadRequest, FloodWait) as e:
            return

# Gestisce il callback per le liste delle cose da fare
@Client.on_callback_query(filters.regex("lst_todo"))
async def lst_todo(client, callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id
    print("todo")
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        if not str(user_id) in data["users"]:
            try:
                await client.edit_message_text(chat_id, message_id, "Non sei registrato, pertanto non puoi accedere alla lista delle cose da fare", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("\U0001F519 Back", callback_data = "menu_todo")]]))
            except FloodWait:
                return
            return
        callback_data = callback_query.data.split(" ")
        search_id = int(callback_data[1])
        if len(callback_data) > 2:
            toggle_id = callback_data[2]
            was_done = data["elements"][toggle_id]["is_done"]
            data["elements"][toggle_id]["is_done"] = not data["elements"][toggle_id]["is_done"]
            toggled_user = data["elements"][toggle_id]["user_id"]
            price = data["elements"][toggle_id]["price"]
            name = data["elements"][toggle_id]["name"]
            quantity = data["elements"][toggle_id]["quantity"]
            if not (str(user_id) in data["credits"] and str(toggled_user) in data["credits"][str(user_id)]):
                data["credits"][str(user_id)] = {str(toggled_user):{"value":0.0}}
            data["credits"][str(user_id)][str(toggled_user)]["value"] += price
            if not toggled_user:
                for id_ in data["users"]:
                    if int(id_) != user_id:
                        try:
                            await client.send_message(int(id_), data["users"][str(user_id)] + " gà crompà el " + name + " x" + str(quantity) + " (Comune). Ringrassia!") 
                        except FloodWait as e:
                            return
            elif toggled_user != user_id:
                try:
                    await client.send_message(toggled_user, data["users"][str(user_id)] + " gà crompà el to " + name + " x" + str(quantity) + ". Ringrassia!") 
                except FloodWait as e:
                    return
            with open('data.json', 'w') as outfile:
                try:
                    json.dump(data, outfile, sort_keys=True, indent=4)
                except Exception as e:
                    print("Unable to write JSON file data.json\n\n" + str(e))
                    return
        elements_filtered = []
        last_index = 0
        for e in sorted(data["elements"].values(), key = lambda k: k["name"]):
            if search_id == -1:
                if (e["user_id"] == user_id or not e["user_id"]) and not e["is_done"]:
                    if e["user_id"]:
                        elements_filtered.append(e)
                    else:
                        elements_filtered.insert(last_index, e)
                        last_index += 1
            elif search_id == user_id:
                if e["user_id"] == search_id and not e["is_done"]:
                    elements_filtered.append(e)
            else:
                if e["user_id"] == search_id and (not e["is_private"] or not search_id) and not e["is_done"]:
                    elements_filtered.append(e)
        elements_processed = []
        for e in elements_filtered:
            cb_data = "todo " + str(search_id)+ " " + [k for k, v in data["elements"].items() if v == e][0]
            elements_processed.append([InlineKeyboardButton(("(C)    " if not e["user_id"] else "") + "\U0001F534 " + e["name"] + " x" + str(e["quantity"]) + " \U0001F534    € " + str(e["price"]), callback_data = cb_data)])
        elements_processed.append([InlineKeyboardButton("\U0001F519 Back", callback_data = "menu_lista")])
        username = ""
        if not search_id:
            username = " in comune"
        elif search_id == -1:
            username = " di " + data["users"][str(user_id)] + " e in comune"
        else:
            username = " di " + data["users"][str(search_id)]
        try:
            await client.edit_message_text(chat_id, message_id, "\U00002B07 **COSE DA FARE" + username.upper() + "** \U00002B07", reply_markup = InlineKeyboardMarkup(elements_processed))
        except (BadRequest, FloodWait) as e:
            return

# Gestisce il callback per le cose da fare
@Client.on_callback_query(filters.regex("todo"))
async def todo(client, callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        callback_data = callback_query.data.split(" ")
        if len(callback_data) > 1:
            del_id = callback_data[1]
            del data["todos"][del_id]
        buttons = []
        for id_, todo in sorted(data["todos"].items(), key = lambda k: k[1]["name"]):
            buttons.append([InlineKeyboardButton(todo["name"], callback_data = "todo " + id_)])
        buttons.append([InlineKeyboardButton("\U0001F519 Back", callback_data = "start")])
        try:
            await client.edit_message_text(chat_id, message_id, "\U00002B07 COSE DA FARE \U00002B07", reply_markup = InlineKeyboardMarkup(buttons))
        except (BadRequest, FloodWait) as e:
            return

# Gestisce il callback per i piatti
@Client.on_callback_query(filters.regex("piatti"))
async def piatti(client, callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        buttons = []
        for dish in sorted(data["dishes"].values(), key = lambda k: k["name"]):
            buttons.append([InlineKeyboardButton(dish["name"], callback_data = " ")])
        buttons.append([InlineKeyboardButton("\U0001F519 Back", callback_data = "start")])
    try:
        await client.edit_message_text(chat_id, callback_query.message.message_id, "Ecco i piatti", reply_markup = InlineKeyboardMarkup(buttons))
    except (BadRequest, FloodWait) as e:
        return

# Gestisce il callback per le contabilità degli utenti
@Client.on_callback_query(filters.regex("contabilita"))
async def contabilita(client, callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        if not str(user_id) in data["users"]:
            await client.edit_message_text(chat_id, message_id, "Non sei registrato, pertanto non puoi accedere alla lista della spesa", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("\U0001F519 Back", callback_data = "menu_contabilita")]]))
            return
        callback_data = callback_query.data.split(" ")
        search_id = callback_data[1]
        credits_filtered = {}
        try:
            for user, credit in data["credits"][search_id].items():
                credits_filtered[user] = credit["value"]
        except KeyError:
            pass
        final_string = "\U0001F4B8 **CONTABILITÀ DI " + data["users"][search_id].upper() + "** \U0001F4B8"
        for (user, value) in credits_filtered.items():
            final_string += "\n\nCredito " + (("Personale" if user == search_id else data["users"][user]) if int(user) else "Comune") + ": € " + str(value)
        try:
            await client.edit_message_text(chat_id, message_id, final_string, reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("\U0001F519 Back", callback_data="menu_contabilita")]]))
        except (BadRequest, FloodWait) as e:
            return

# Gestisce il comando /add per aggiungere un elemento ad una lista
@Client.on_message(filters.command(["add"]))
async def add(client, message):
    chat_id = message.chat.id
    message_data = message.text.split(" ")
    user_id = message.from_user.id
    if len(message_data) < 6:
        try:
            await client.send_message(chat_id, "Sintassi del comando errata! Usa /help per una spiegazione del comando")
        except FloodWait:
            return
        return
    if not (user_id in config.admin_users):
        try:
            await client.send_message(chat_id, "Non hai i privilegi necessari per eseguire questo comando!")
        except FloodWait:
            return
        return
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        name = ""
        for n in message_data[5:]:
            name += n + " "
        data["elements"][str(int(max(data["elements"], key=int)) + 1) if len(data["elements"]) else "0"] = {"is_done": False, "is_private": True if message_data[2].lower() == "private" else False, "name": name[:-1], "price":float(message_data[3]), "quantity":int(message_data[4]), "user_id":user_id if message_data[1].lower()=="me" else 0}
        with open('data.json', 'w') as outfile:
            try:
                json.dump(data, outfile, sort_keys=True, indent=4)
            except Exception as e:
                print("Unable to write JSON file data.json\n\n" + str(e))
                return
        try:
            await client.send_message(chat_id, "Elemento aggiunto con successo alla lista!")
        except FloodWait:
            return

# Gestisce il comando /delete per eliminare un elemento
@Client.on_message(filters.command(["delete"]))
async def delete(client, message):
    chat_id = message.chat.id
    message_data = message.text.split(" ")
    user_id = message.from_user.id
    if len(message_data) < 3:
        await client.send_message(chat_id, "Sintassi del comando errata! Usa /help per una spiegazione del comando")
        return
    if not (user_id in config.admin_users):
        await client.send_message(chat_id, "Non hai i privilegi necessari per eseguire questo comando!")
        return
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        name = ""
        for n in message_data[2:]:
            name += n + " " 
        for i, e in data["elements"].items():
            if e["name"].lower() == name[:-1].lower() and e["quantity"] == int(message_data[1]) and (e["user_id"] == user_id or not e["user_id"]):
                del data["elements"][i]
                try:
                    await client.send_message(chat_id, "Elemento eliminato con successo dalla lista!")
                except FloodWait:
                    return
                break
        with open('data.json', 'w') as outfile:
            try:
                json.dump(data, outfile, sort_keys=True, indent=4)
            except Exception as e:
                print("Unable to write JSON file data.json\n\n" + str(e))
                return
    
# Gestisce il comando /reset per impostare a zero il valore del credito di un utente verso un altro utente
@Client.on_message(filters.command(["reset"]))
async def reset(client, message):
    chat_id = message.chat.id
    message_data = message.text.split(" ")
    user_id = message.from_user.id
    if len(message_data) != 3:
        await client.send_message(chat_id, "Sintassi del comando errata! Usa /help per una spiegazione del comando")
    if not (user_id in config.admin_users):
        await client.send_message(chat_id, "Non hai i privilegi necessari per eseguire questo comando!")
        return
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
    try:
        data["credits"][message_data[1]][message_data[2]]["value"] = 0.0
    except KeyError:
        try:
            await client.send_message(chat_id, "Impossibile resettare il credito. Forse hai inserito un id che non esiste")
        except FloodWait:
            return
        return
    try:
        await client.send_message(chat_id, "Credito resettato con successo!")
    except FloodWait:
        return
    with open('data.json', 'w') as outfile:
        try:
            json.dump(data, outfile, sort_keys=True, indent=4)
        except Exception as e:
            print("Unable to write JSON file data.json\n\n" + str(e))
            return

#Gestisce il comando /reset per impostare a zero il valore del credito di un utente verso un altro utente
@Client.on_message(filters.command(["reset_user"]))
async def reset(client, message):
    chat_id = message.chat.id
    message_data = message.text.split(" ")
    user_id = message.from_user.id
    if len(message_data) != 2:
        await client.send_message(chat_id, "Sintassi del comando errata! Usa /help per una spiegazione del comando")
    if not (user_id in config.admin_users):
        await client.send_message(chat_id, "Non hai i privilegi necessari per eseguire questo comando!")
        return
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
    try:
        data["credits"][message_data[1]] = dict.fromkeys(data["credits"][message_data[1]], {"value": 0.0})
    except KeyError:
        try:
            await client.send_message(chat_id, "Impossibile resettare il credito. Forse hai inserito un id che non esiste")
        except FloodWait:
            return
        return
    try:
        await client.send_message(chat_id, "Credito resettato con successo!")
    except FloodWait:
        return
    with open('data.json', 'w') as outfile:
        try:
            json.dump(data, outfile, sort_keys=True, indent=4)
        except Exception as e:
            print("Unable to write JSON file data.json\n\n" + str(e))
            return

# Gestisce il comando /set per impostare il credito nei confronti di un utente
@Client.on_message(filters.command(["set"]))
async def set(client, message):
    chat_id = message.chat.id
    message_data = message.text.split(" ")
    user_id = message.from_user.id
    if len(message_data) != 4:
        try:
            await client.send_message(chat_id, "Sintassi del comando errata! Usa /help per una spiegazione del comando")
        except FloodWait:
            return
        return
    if not (user_id in config.admin_users):
        try:
            await client.send_message(chat_id, "Non hai i privilegi necessari per eseguire questo comando!")
        except FloodWait:
            return
        return
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        try:
            data["credits"][message_data[1]][message_data[2]]["value"] = float(message_data[3])
        except KeyError:
            try:
                await client.send_message(chat_id, "Impossibile resettare il credito. Forse hai inserito un id che non esiste")
            except FloodWait:
                return
            return
        with open('data.json', 'w') as outfile:
            try:
                json.dump(data, outfile, sort_keys=True, indent=4)
            except Exception as e:
                print("Unable to write JSON file data.json\n\n" + str(e))
                return
        try:
            await client.send_message(chat_id, "Credito impostato con successo!")
        except FloodWait:
            return

# Gestisce il comando /add_todo per aggiungere una cosa da fare
@Client.on_message(filters.command(["add_todo"]))
async def add_todo(client, message):
    chat_id = message.chat.id
    message_data = message.text.split(" ")
    user_id = message.from_user.id
    if len(message_data) < 2:
        try:
            await client.send_message(chat_id, "Sintassi del comando errata! Usa /help per una spiegazione del comando")
        except FloodWait:
            return
        return
    if not (user_id in config.admin_users):
        try:
            await client.send_message(chat_id, "Non hai i privilegi necessari per eseguire questo comando!")
        except FloodWait:
            return
        return
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        name = ""
        for n in message_data[1:]:
            name += n + " "
        data["todos"][str(int(max(data["todos"], key=int)) + 1) if len(data["todos"]) else "0"] = {"name":name}
        with open('data.json', 'w') as outfile:
            try:
                json.dump(data, outfile, sort_keys=True, indent=4)
            except Exception as e:
                print("Unable to write JSON file data.json\n\n" + str(e))
                return
        try:
            await client.send_message(chat_id, "Cosa da fare aggiunta con successo!")
        except FloodWait:
            return


# Gestisce il comando /add_user per aggiungere un utente
@Client.on_message(filters.command(["add_user"]))
async def add_user(client, message):
    chat_id = message.chat.id
    message_data = message.text.split(" ")
    user_id = message.from_user.id
    if len(message_data) != 3:
        try:
            await client.send_message(chat_id, "Sintassi del comando errata! Usa /help per una spiegazione del comando")
        except FloodWait:
            return
        return
    if not (user_id in config.admin_users):
        try:
            await client.send_message(chat_id, "Non hai i privilegi necessari per eseguire questo comando!")
        except FloodWait:
            return
        return
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        data["users"][message_data[2]] = message_data[1]
        with open('data.json', 'w') as outfile:
            try:
                json.dump(data, outfile, sort_keys=True, indent=4)
            except Exception as e:
                print("Unable to write JSON file data.json\n\n" + str(e))
                return
        try:
            await client.send_message(chat_id, "Utente aggiunto con successo!")
        except FloodWait:
            return

# Gestisce il comando /delete_user per eliminare un utente
@Client.on_message(filters.command(["delete_user"]))
async def delete_user(client, message):
    chat_id = message.chat.id
    message_data = message.text.split(" ")
    user_id = message.from_user.id
    if len(message_data) != 2:
        try:
            await client.send_message(chat_id, "Sintassi del comando errata! Usa /help per una spiegazione del comando")
        except FloodWait:
            return
        return
    if not (user_id in config.admin_users):
        try:
            await client.send_message(chat_id, "Non hai i privilegi necessari per eseguire questo comando!")
        except FloodWait:
            return
        return
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        try:
            del data["users"][message_data[1]]
        except KeyError:
            try:
                await client.send_message(chat_id, "Impossibile eliminare l'utente: id non esistente")
            except FloodWait:
                return
        with open('data.json', 'w') as outfile:
            try:
                json.dump(data, outfile, sort_keys=True, indent=4)
            except Exception as e:
                print("Unable to write JSON file data.json\n\n" + str(e))
                return
        try:
            await client.send_message(chat_id, "Utente eliminato con successo!")
        except FloodWait:
            return

# Gestisce il comando /add_dish per aggiungere un piatto
@Client.on_message(filters.command(["add_dish"]))
async def add_dish(client, message):
    chat_id = message.chat.id
    message_data = message.text.split(" ")
    user_id = message.from_user.id
    if len(message_data) < 2:
        try:
            await client.send_message(chat_id, "Sintassi del comando errata! Usa /help per una spiegazione del comando")
        except FloodWait:
            return
        return
    if not (user_id in config.admin_users):
        try:
            await client.send_message(chat_id, "Non hai i privilegi necessari per eseguire questo comando!")
        except FloodWait:
            return
        return
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        name = ""
        for n in message_data[1:]:
            name += n + " "
        data["dishes"][str(int(max(data["dishes"], key=int)) + 1) if len(data["dishes"]) else "0"] = {"name":name}
        with open('data.json', 'w') as outfile:
            try:
                json.dump(data, outfile, sort_keys=True, indent=4)
            except Exception as e:
                print("Unable to write JSON file data.json\n\n" + str(e))
                return
        try:
            await client.send_message(chat_id, "Piatto aggiunto con successo!")
        except FloodWait:
            return

# Gestisce il comando /delete_dish per eliminare un piatto
@Client.on_message(filters.command(["delete_dish"]))
async def delete_dish(client, message):
    chat_id = message.chat.id
    message_data = message.text.split(" ")
    user_id = message.from_user.id
    if len(message_data) < 2:
        await client.send_message(chat_id, "Sintassi del comando errata! Usa /help per una spiegazione del comando")
        return
    if not (user_id in config.admin_users):
        await client.send_message(chat_id, "Non hai i privilegi necessari per eseguire questo comando!")
        return
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        name = ""
        for n in message_data[1:]:
            name += n + " "
        for i, d in data["dishes"].items():
            if name.lower() in d["name"].lower():
                del data["dishes"][i]
                try:
                    await client.send_message(chat_id, "Piatto eliminato con successo!")
                except FloodWait:
                    return
                break
        with open('data.json', 'w') as outfile:
            try:
                json.dump(data, outfile, sort_keys=True, indent=4)
            except Exception as e:
                print("Unable to write JSON file data.json\n\n" + str(e))
                return
    


# Gestisce il comando /get_ids per ottenere gli id degli utenti attualmente registrati
@Client.on_message(filters.command(["get_ids"]))
async def get_user_ids(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not (user_id in config.admin_users):
        await client.send_message(chat_id, "Non hai i privilegi necessari per eseguire questo comando!")
        return
    with open("data.json") as openfile:
        try:
            data_json = openfile.read()
            data = json.loads(data_json)
        except Exception as e:
            print("Cannot load JSON file data.json\n\n" + str(e))
            return
        final_string = ""
        for id_, user in data["users"].items():
            final_string += "Utente: " + user + "\nID: " + id_ + "\n\n"
        try:
            await client.send_message(chat_id, final_string)
        except FloodWait:
            return

# Gestisce il comando /get_id per ottenere il proprio id utente
@Client.on_message(filters.command(["get_id"]))
async def suqi(client, message):
    chat_id = message.chat.id
    await client.send_message(chat_id, str(message.from_user.id))

# Gestisce il comando /get_chat_id per ottenere l'id della chat corrente
#@Client.on_message(filters.command(["get_chat_id"]))
#async def get_chat_id(client, message):
#   chat_id = message.chat.id
#   await client.send_message(chat_id, str(chat_id))
