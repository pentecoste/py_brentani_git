admin_users = [420032395,886901334,186728020]

API_TOKEN = "1947203463:AAHzBlJOvL4it0VJ2PsBMnd-8qnoNizlVZY"

help_message = """Hai bisogno di aiuto?

/start\n- Accedi alle funzioni del bot

/add Utente Private Quantita GiorniScadenza NomeElemento\n- Aggiungi un elemento alla lista\nExample: /add me private 3 0 Maccheroni\nExample: /add all public 2 5 Albicocche Marce (se il prodotto non ha scadenza o ha scadenza trascurabile mettere 0 come giorni di scadenza, di modo che venga ignorato)

/delete Quantità NomeElemento\n- Elimina gli elementi con un certo nome dalla lista\nExample: /delete 2 Carciofo OGM Del Brenta (la quantità è da specificare per ridurre le ambiguità nel caso si volessero tenere due elementi con nomi uguali ma quantità diverse)

/get_ids\n- Ottieni gli id di tutti gli utenti registrati (sono molto utili)

/get_id\n- Ottieni il tuo id (utile ad esempio per capire che id devi mettere nell'add_user)

/add_user NomeUtente IdUtente\n- Aggiungi un utente\nExample: /add_user Messi 10 (l'id deve essere quello associato al proprio account telegram, altrimenti non va una tega. Facciamo finta che Messi abbia id 10 ok?)

/delete_user IdUtente\n- Elimina un utente in base all'id\nExample: /delete_user 10 (elimina Messi)

/add_todo nome_todo\n- Aggiunge una cosa da fare con un certo nome_todo\nExample: /add_todo Creare una canzone con solo Matteo come parola"""
