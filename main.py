import pg8000.native
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()
DB_PASSWORD = os.environ["TODO_DB_PASSWORD"]

app = FastAPI()

def apri_connessione():
	return pg8000.native.Connection(
		user="todo_user",
		password = DB_PASSWORD,
		database = "todo_db",
		host = "localhost",
	)
	
class NuovaAttivita(BaseModel):
	testo:str
	
class ModificaAttivita(BaseModel):
	fatta:bool

def riga_to_dict(r):
	return {"id": r[0], "testo": r[1], "fatta": r[2], "creata_il": str(r[3])}

@app.get("/")
def pagina():
	return FileResponse("static/index.html")

@app.get("/attivita")
def elenco_attivita():
	con = apri_connessione()
	try:
		righe = con.run(
			"SELECT id, testo, fatta, creata_il FROM attivita ORDER BY id"
		)
	finally:
		con.close()
	return [
		{"id": r[0], "testo": r[1], "fatta": r[2], "creata_il": str(r[3])}
		for r in righe
		]

@app.post("/attivita")
def crea_attivita(nuova: NuovaAttivita):
	con = apri_connessione()
	try:
		righe = con.run(
			"INSERT INTO attivita (testo) VALUES (:testo) "
			"RETURNING id, testo, fatta, creata_il",
			testo = nuova.testo,
		)
	finally:
		con.close()
	return riga_to_dict(righe[0])
	
@app.patch("/attivita/{attivita_id}")
def modifica_attivita(attivita_id: int, modifica: ModificaAttivita):
	con = apri_connessione()
	try:
		righe = con.run(
			"UPDATE attivita SET fatta = :fatta WHERE id = :id "
			"RETURNING id, testo, fatta, creata_il",
			fatta=modifica.fatta,
			id=attivita_id,
		)
	finally:
		con.close()
	if not righe:
		raise HTTPException(status_code=404, detail="Attivita non trovata")
	return riga_to_dict(righe[0])
	
@app.delete("/attivita/{attivita_id}")
def cancella_attivita(attivita_id: int):
	con = apri_connessione()
	try:
		righe = con.run(
			"DELETE FROM attivita WHERE id = :id RETURNING id",
			id=attivita_id,
		)
	finally:
		con.close()
	if not righe:
		raise HTTPException(status_code=404, detail="Attivita non trovata")
	return {"cancellata": attivita_id}
