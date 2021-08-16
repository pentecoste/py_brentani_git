admin_users = []

API_TOKEN = ""

help_message = """Hai bisogno di aiuto?

/start\n- Accedi alle funzioni del bot

/add Quantita NomeElemento Utente Private Prezzo\n- Aggiungi un elemento alla lista\nExample: /add 3 Maccheroni me private 5.49\nExample: /add 2 Albicocche all public 1.20

/delete Quantità NomeElemento\n- Elimina gli elementi con un certo nome dalla lista\nExample: /delete 2 Carciofo (la quantità è da specificare per ridurre le ambiguità nel caso si volessero tenere due elementi con nomi uguali ma quantità diverse)

/reset Utente Credito\n- Resetta il credito di un utente nei confronti di un altro utente\nExample: /reset 109239450 0 (0 = Utente Comune)\nExample: /reset 204924391 958885421

/set Utente Credito Valore\n- Imposta ad un certo valore il credito di un utente nei confronti di un altro utente\nExample: /set 109239450 0 10.0 (0 = Utente Comune)

/get_ids\n- Ottieni gli id di tutti gli utenti registrati (sono molto utili)

/get_id\n- Ottieni il tuo id (utile ad esempio per capire che id devi mettere nell'add_user)

/add_user NomeUtente IdUtente\n- Aggiungi un utente\nExample: /add_user Messi 10 (l'id deve essere quello associato al proprio account telegram, altrimenti non va una tega. Facciamo finta che Messi abbia id 10 ok?)

/delete_user IdUtente\n- Elimina un utente in base all'id\nExample: /delete_user 10 (elimina Messi)"""
