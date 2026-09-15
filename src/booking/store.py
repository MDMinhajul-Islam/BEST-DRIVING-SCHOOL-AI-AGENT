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
   CREATE TABLE IF NOT EXISTS internal_services(package_id TEXT PRIMARY KEY,name TEXT NOT NULL,session_plan TEXT,auto_schedulable INTEGER NOT NULL,source TEXT NOT NULL);
   CREATE TABLE IF NOT EXISTS availability_rules(id TEXT PRIMARY KEY,package_id TEXT NOT NULL,weekday INTEGER NOT NULL,start_time TEXT NOT NULL,end_time TEXT NOT NULL,effective_start TEXT NOT NULL,effective_end TEXT,capacity INTEGER NOT NULL,active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
   CREATE TABLE IF NOT EXISTS blackouts(id TEXT PRIMARY KEY,package_id TEXT NOT NULL,start TEXT NOT NULL,end TEXT NOT NULL,note TEXT,active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL);
   CREATE TABLE IF NOT EXISTS booking_groups(id TEXT PRIMARY KEY,scope TEXT NOT NULL,package_id TEXT NOT NULL,customer_name TEXT NOT NULL,customer_email TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
   CREATE TABLE IF NOT EXISTS internal_sessions(uid TEXT PRIMARY KEY,group_id TEXT NOT NULL,appointment_ref TEXT UNIQUE NOT NULL,package_id TEXT NOT NULL,start TEXT NOT NULL,end TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,cancelled_at TEXT,FOREIGN KEY(group_id) REFERENCES booking_groups(id));
   CREATE TABLE IF NOT EXISTS internal_history(id TEXT PRIMARY KEY,at TEXT NOT NULL,action TEXT NOT NULL,object_type TEXT NOT NULL,object_id TEXT NOT NULL,metadata TEXT NOT NULL);
   CREATE INDEX IF NOT EXISTS ix_internal_sessions_time ON internal_sessions(status,start,end);
   CREATE INDEX IF NOT EXISTS ix_availability_lookup ON availability_rules(active,package_id,weekday,effective_start,effective_end);
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
