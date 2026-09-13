"""Restart-safe SQLite ledger; one durable volume, no process-only booking metadata."""
import sqlite3,json,uuid
from contextlib import contextmanager
from datetime import datetime,timezone
class Store:
 def __init__(self,path):
  self.path=str(path)
  from pathlib import Path
  Path(path).parent.mkdir(parents=True,exist_ok=True)
  with self.connect() as db:db.executescript('''
   PRAGMA journal_mode=WAL;
   CREATE TABLE IF NOT EXISTS slots(ref TEXT PRIMARY KEY,scope TEXT,mode TEXT,package TEXT,duration INTEGER,start TEXT,end TEXT,expires REAL,UNIQUE(scope,mode,package,duration,start));
   CREATE TABLE IF NOT EXISTS appointments(ref TEXT PRIMARY KEY,scope TEXT,mode TEXT,package TEXT,idx INTEGER,uid TEXT,data TEXT);
   CREATE TABLE IF NOT EXISTS actions(key TEXT PRIMARY KEY,scope TEXT,mode TEXT,operation TEXT,state TEXT,result TEXT);
   CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,at TEXT,operation TEXT,mode TEXT,package TEXT,idx INTEGER,status TEXT);
   CREATE TABLE IF NOT EXISTS mock_provider(uid TEXT PRIMARY KEY,start TEXT,end TEXT,status TEXT);
   CREATE TABLE IF NOT EXISTS locks(target TEXT PRIMARY KEY,owner TEXT);
  ''')
 @contextmanager
 def connect(self):
  db=sqlite3.connect(self.path,timeout=30);db.row_factory=sqlite3.Row
  try:yield db;db.commit()
  except:db.rollback();raise
  finally:db.close()
 def audit(self,operation,mode,package,idx,status):
  with self.connect() as db:db.execute('INSERT INTO audit(at,operation,mode,package,idx,status) VALUES(?,?,?,?,?,?)',(datetime.now(timezone.utc).isoformat(),operation,mode,package,idx,status))
 def save_appointment(self,ref,scope,mode,package,idx,data):
  with self.connect() as db:db.execute('INSERT OR REPLACE INTO appointments VALUES(?,?,?,?,?,?,?)',(ref,scope,mode,package,idx,data['provider_uid'],json.dumps(data)))
 def get_appointment(self,ref,scope,mode):
  with self.connect() as db:r=db.execute('SELECT * FROM appointments WHERE ref=? AND scope=? AND mode=?',(ref,scope,mode)).fetchone()
  if r:return dict(r)|{'data':json.loads(r['data'])}
 def claim(self,key,scope,mode,operation):
  with self.connect() as db:
   db.execute('BEGIN IMMEDIATE');r=db.execute('SELECT * FROM actions WHERE key=?',(key,)).fetchone()
   if r:return dict(r)
   db.execute('INSERT INTO actions VALUES(?,?,?,?,?,?)',(key,scope,mode,operation,'pending',None))
  return None
 def finish(self,key,result):
  with self.connect() as db:db.execute('UPDATE actions SET state=?,result=? WHERE key=?',('complete',json.dumps(result),key))
 def lock(self,target,owner):
  with self.connect() as db:
   db.execute('BEGIN IMMEDIATE');r=db.execute('INSERT OR IGNORE INTO locks VALUES(?,?)',(target,owner))
   return r.rowcount==1
 def unlock(self,target,owner):
  with self.connect() as db:db.execute('DELETE FROM locks WHERE target=? AND owner=?',(target,owner))
