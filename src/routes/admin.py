"""Authenticated same-application admin dashboard for the internal calendar MVP."""
import os,json,hmac,hashlib,secrets,base64,time,uuid,re
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from fastapi import Request
from fastapi.responses import HTMLResponse,JSONResponse
from src.booking.validators import BookingError,date_bounds

COOKIE='bds_admin_session'
def _b64(b):return base64.urlsafe_b64encode(b).decode().rstrip('=')
def _unb64(s):return base64.urlsafe_b64decode(s+'='*(-len(s)%4))
def _password(password,encoded):
 try:
  name,it,salt,want=encoded.split('$');got=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),int(it)).hex()
  return name=='pbkdf2_sha256' and int(it)>=200000 and hmac.compare_digest(got,want)
 except Exception:return False
def make_password_hash(password,iterations=310000):
 salt=secrets.token_bytes(16);return f'pbkdf2_sha256${iterations}${salt.hex()}${hashlib.pbkdf2_hmac("sha256",password.encode(),salt,iterations).hex()}'
def _admin_stamp(value):
 if not isinstance(value,str):raise BookingError('INVALID_TIME')
 try:parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
 except ValueError:raise BookingError('INVALID_TIME')
 if parsed.tzinfo is None:parsed=parsed.replace(tzinfo=ZoneInfo('America/Chicago'))
 return parsed.astimezone(timezone.utc)

from src.routes.admin_page import PAGE

def attach_admin(app,service):
 username=os.getenv('ADMIN_USERNAME','');password_hash=os.getenv('ADMIN_PASSWORD_HASH','');session_secret=os.getenv('ADMIN_SESSION_SECRET','');secure=os.getenv('ADMIN_COOKIE_SECURE','true').lower()=='true'
 if not username or not password_hash or len(session_secret)<32:raise ValueError('Internal mode requires ADMIN_USERNAME, ADMIN_PASSWORD_HASH and 32+ character ADMIN_SESSION_SECRET')
 def sign(payload):
  raw=_b64(json.dumps(payload,separators=(',',':')).encode());return raw+'.'+hmac.new(session_secret.encode(),raw.encode(),hashlib.sha256).hexdigest()
 def session(req):
  try:
   raw,sig=req.cookies.get(COOKIE,'').rsplit('.',1)
   if not hmac.compare_digest(sig,hmac.new(session_secret.encode(),raw.encode(),hashlib.sha256).hexdigest()):return None
   p=json.loads(_unb64(raw));return p if p['exp']>=time.time() and p['u']==username else None
  except Exception:return None
 def auth(req,csrf=False):
  s=session(req)
  if not s or (csrf and not hmac.compare_digest(req.headers.get('X-CSRF-Token',''),s['csrf'])):raise BookingError('AUTHENTICATION_FAILURE')
  return s
 def safe_error(code=401):return JSONResponse({'success':False,'error':'Unauthorized'},status_code=code)
 @app.get('/admin',response_class=HTMLResponse)
 def page():return PAGE
 @app.post('/admin/api/login')
 async def login(req:Request):
  try:b=await req.json()
  except Exception:return safe_error(400)
  if not isinstance(b,dict) or not hmac.compare_digest(str(b.get('username','')),username) or not _password(str(b.get('password','')),password_hash):return safe_error()
  csrf=secrets.token_urlsafe(24);cookie=sign({'u':username,'csrf':csrf,'exp':int(time.time()+28800)});r=JSONResponse({'success':True,'csrf':csrf});r.set_cookie(COOKIE,cookie,httponly=True,secure=secure,samesite='strict',max_age=28800,path='/admin');return r
 @app.post('/admin/api/logout')
 def logout(req:Request):
  try:auth(req,True)
  except BookingError:return safe_error()
  r=JSONResponse({'success':True});r.delete_cookie(COOKIE,path='/admin');return r
 @app.get('/admin/api/summary')
 def summary(req:Request):
  try:s=auth(req)
  except BookingError:return safe_error()
  today=datetime.now(timezone.utc).astimezone(ZoneInfo('America/Chicago')).date().isoformat();day_start,day_end=date_bounds(today)
  with service.store.connect() as db:
   vals={'today':db.execute("SELECT count(*) FROM internal_sessions WHERE status='accepted' AND start>=? AND start<?",(day_start.isoformat().replace('+00:00','Z'),day_end.isoformat().replace('+00:00','Z'))).fetchone()[0],'upcoming':db.execute("SELECT count(*) FROM internal_sessions WHERE status='accepted' AND start>=?",(datetime.now(timezone.utc).isoformat(),)).fetchone()[0],'active':db.execute("SELECT count(*) FROM internal_sessions WHERE status='accepted'").fetchone()[0],'cancelled':db.execute("SELECT count(*) FROM internal_sessions WHERE status='cancelled'").fetchone()[0],'rules':db.execute("SELECT count(*) FROM availability_rules WHERE active=1").fetchone()[0],'blackouts':db.execute("SELECT count(*) FROM blackouts WHERE active=1").fetchone()[0]}
  return vals|{'csrf':s['csrf'],'timezone':'America/Chicago'}
 @app.get('/admin/api/services')
 def services(req:Request):
  try:auth(req)
  except BookingError:return safe_error()
  with service.store.connect() as db:rows=db.execute('SELECT package_id,name,session_plan FROM internal_services WHERE auto_schedulable=1 ORDER BY name').fetchall()
  return {'items':[{'package_id':r['package_id'],'name':r['name'],'session_plan':json.loads(r['session_plan'])} for r in rows]}
 @app.get('/admin/api/bookings')
 def bookings(req:Request,q:str='',status:str=''):
  try:auth(req)
  except BookingError:return safe_error()
  if len(q)>100 or status not in ('','accepted','cancelled'):return JSONResponse({'error':'Invalid filter'},400)
  sql='SELECT s.*,g.customer_name,g.customer_email,g.scope,a.idx AS session_index FROM internal_sessions s JOIN booking_groups g ON g.id=s.group_id LEFT JOIN appointments a ON a.ref=s.appointment_ref WHERE 1=1';args=[]
  if status:sql+=' AND s.status=?';args.append(status)
  if q:sql+=' AND (s.appointment_ref LIKE ? OR g.customer_name LIKE ? OR g.customer_email LIKE ? OR s.package_id LIKE ?)';args += ['%'+q+'%']*4
  with service.store.connect() as db:items=[dict(r) for r in db.execute(sql+' ORDER BY s.start LIMIT 500',args)]
  return {'items':items}
 @app.get('/admin/api/availability')
 def rules(req:Request):
  try:auth(req)
  except BookingError:return safe_error()
  with service.store.connect() as db:return {'items':[dict(r) for r in db.execute('SELECT * FROM availability_rules ORDER BY weekday,start_time')]}
 @app.post('/admin/api/availability')
 async def add_rule(req:Request):
  try:auth(req,True)
  except BookingError:return safe_error()
  try:b=await req.json();pid=b['package_id'];wd=b['weekday'];start=b['start_time'];end=b['end_time'];es=b['effective_start'];ee=b.get('effective_end');cap=b['capacity']
  except (KeyError,ValueError,TypeError):return JSONResponse({'error':'Invalid rule'},400)
  try:sv=datetime.strptime(start,'%H:%M');ev=datetime.strptime(end,'%H:%M');esv=datetime.strptime(es,'%Y-%m-%d');eev=datetime.strptime(ee,'%Y-%m-%d') if ee else None
  except (ValueError,TypeError):return JSONResponse({'error':'Invalid rule'},400)
  if not isinstance(pid,str) or len(pid)>100 or type(wd) is not int or wd not in range(7) or sv>=ev or (eev and eev<esv) or type(cap) is not int or cap<1 or cap>100:return JSONResponse({'error':'Invalid rule'},400)
  at=datetime.now(timezone.utc).isoformat();rid='AR-'+uuid.uuid4().hex
  with service.store.connect() as db:
   service_row=db.execute('SELECT session_plan FROM internal_services WHERE package_id=? AND auto_schedulable=1',(pid,)).fetchone() if pid!='*' else None
   if pid!='*' and not service_row:return JSONResponse({'error':'Unsupported package'},400)
   minimum=min(json.loads(service_row['session_plan'])) if service_row else 30
   if int((ev-sv).total_seconds()/60)<minimum:return JSONResponse({'error':f'Window must fit at least one {minimum}-minute session'},400)
   db.execute('INSERT INTO availability_rules VALUES(?,?,?,?,?,?,?,?,?,?,?)',(rid,pid,wd,start,end,es,ee,cap,1,at,at));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'availability_created','availability_rule',rid,json.dumps({'package_id':pid,'capacity':cap})))
  return {'success':True,'id':rid}
 @app.post('/admin/api/availability/{rid}/deactivate')
 def disable_rule(rid:str,req:Request):
  try:auth(req,True)
  except BookingError:return safe_error()
  at=datetime.now(timezone.utc).isoformat()
  with service.store.connect() as db:
   if not db.execute('SELECT 1 FROM availability_rules WHERE id=?',(rid,)).fetchone():return JSONResponse({'error':'Rule not found'},404)
   db.execute('UPDATE availability_rules SET active=0,updated_at=? WHERE id=?',(at,rid));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'availability_disabled','availability_rule',rid,'{}'))
  return {'success':True}
 @app.post('/admin/api/availability/{rid}/activate')
 def activate_rule(rid:str,req:Request):
  try:auth(req,True)
  except BookingError:return safe_error()
  at=datetime.now(timezone.utc).isoformat()
  with service.store.connect() as db:
   if not db.execute('SELECT 1 FROM availability_rules WHERE id=?',(rid,)).fetchone():return JSONResponse({'error':'Rule not found'},404)
   db.execute('UPDATE availability_rules SET active=1,updated_at=? WHERE id=?',(at,rid));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'availability_activated','availability_rule',rid,'{}'))
  return {'success':True}
 @app.post('/admin/api/availability/{rid}')
 async def edit_rule(rid:str,req:Request):
  try:auth(req,True);b=await req.json();start=b['start_time'];end=b['end_time'];cap=b['capacity']
  except BookingError:return safe_error()
  except (KeyError,TypeError):return JSONResponse({'error':'Invalid rule'},400)
  try:sv=datetime.strptime(start,'%H:%M');ev=datetime.strptime(end,'%H:%M')
  except (ValueError,TypeError):return JSONResponse({'error':'Invalid rule'},400)
  if sv>=ev or type(cap) is not int or cap<1 or cap>100:return JSONResponse({'error':'Invalid rule'},400)
  at=datetime.now(timezone.utc).isoformat()
  with service.store.connect() as db:
   existing=db.execute('SELECT r.*,s.session_plan FROM availability_rules r LEFT JOIN internal_services s ON s.package_id=r.package_id WHERE r.id=?',(rid,)).fetchone()
   if not existing:return JSONResponse({'error':'Rule not found'},404)
   minimum=min(json.loads(existing['session_plan'])) if existing['session_plan'] else 30
   if int((ev-sv).total_seconds()/60)<minimum:return JSONResponse({'error':f'Window must fit at least one {minimum}-minute session'},400)
   db.execute('UPDATE availability_rules SET start_time=?,end_time=?,capacity=?,updated_at=? WHERE id=?',(start,end,cap,at,rid));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'availability_changed','availability_rule',rid,json.dumps({'capacity':cap})))
  return {'success':True}
 @app.get('/admin/api/blackouts')
 def blackouts(req:Request):
  try:auth(req)
  except BookingError:return safe_error()
  with service.store.connect() as db:return {'items':[dict(r) for r in db.execute('SELECT * FROM blackouts ORDER BY start')]}
 @app.post('/admin/api/blackouts')
 async def add_blackout(req:Request):
  try:auth(req,True)
  except BookingError:return safe_error()
  try:b=await req.json();pid=b.get('package_id','*');start=_admin_stamp(b['start']);end=_admin_stamp(b['end']);note=b.get('note','')
  except (BookingError,KeyError,TypeError):return JSONResponse({'error':'Invalid blackout'},400)
  if end<=start or not isinstance(pid,str) or not pid or len(pid)>100 or not isinstance(note,str) or len(note)>300:return JSONResponse({'error':'Invalid blackout'},400)
  bid='BO-'+uuid.uuid4().hex;at=datetime.now(timezone.utc).isoformat()
  with service.store.connect() as db:
   if pid!='*' and not db.execute('SELECT 1 FROM internal_services WHERE package_id=? AND auto_schedulable=1',(pid,)).fetchone():return JSONResponse({'error':'Unsupported package'},400)
   db.execute('INSERT INTO blackouts VALUES(?,?,?,?,?,?,?)',(bid,pid,start.isoformat().replace('+00:00','Z'),end.isoformat().replace('+00:00','Z'),note,1,at));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'blackout_created','blackout',bid,json.dumps({'package_id':pid})))
  return {'success':True,'id':bid}
 @app.post('/admin/api/blackouts/{bid}/deactivate')
 def disable_blackout(bid:str,req:Request):
  try:auth(req,True)
  except BookingError:return safe_error()
  at=datetime.now(timezone.utc).isoformat()
  with service.store.connect() as db:
   if not db.execute('SELECT 1 FROM blackouts WHERE id=?',(bid,)).fetchone():return JSONResponse({'error':'Blackout not found'},404)
   db.execute('UPDATE blackouts SET active=0 WHERE id=?',(bid,));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'blackout_disabled','blackout',bid,'{}'))
  return {'success':True}
 @app.post('/admin/api/blackouts/{bid}/activate')
 def activate_blackout(bid:str,req:Request):
  try:auth(req,True)
  except BookingError:return safe_error()
  at=datetime.now(timezone.utc).isoformat()
  with service.store.connect() as db:
   if not db.execute('SELECT 1 FROM blackouts WHERE id=?',(bid,)).fetchone():return JSONResponse({'error':'Blackout not found'},404)
   db.execute('UPDATE blackouts SET active=1 WHERE id=?',(bid,));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'blackout_activated','blackout',bid,'{}'))
  return {'success':True}
 @app.post('/admin/api/bookings/{ref}/cancel')
 def admin_cancel(ref:str,req:Request):
  try:auth(req,True)
  except BookingError:return safe_error()
  with service.store.connect() as db:r=db.execute("SELECT * FROM appointments WHERE ref=? AND mode='internal'",(ref,)).fetchone()
  if not r:return JSONResponse({'error':'Booking not found'},404)
  try:data=service.adapter.cancel_booking(r['uid']);service.store.save_appointment(ref,r['scope'],'internal',r['package'],r['idx'],data)
  except BookingError as e:return JSONResponse({'error':e.code},409)
  return {'success':True,'booking_status':'cancelled','refund_issued':False}
 @app.get('/admin/api/bookings/{ref}')
 def booking_detail(ref:str,req:Request):
  try:auth(req)
  except BookingError:return safe_error()
  with service.store.connect() as db:
   row=db.execute('SELECT s.*,g.customer_name,g.customer_email,g.scope,g.created_at AS group_created_at FROM internal_sessions s JOIN booking_groups g ON g.id=s.group_id WHERE s.appointment_ref=?',(ref,)).fetchone()
   if not row:return JSONResponse({'error':'Booking not found'},404)
   sessions=[dict(x) for x in db.execute('SELECT appointment_ref,start,end,status FROM internal_sessions WHERE group_id=? ORDER BY start',(row['group_id'],))];history=[dict(x) for x in db.execute("SELECT at,action,object_type,object_id,metadata FROM internal_history WHERE object_id IN (?,?) ORDER BY at",(row['group_id'],row['uid']))]
  return {'booking':dict(row),'group_sessions':sessions,'history':history,'timezone':'America/Chicago'}
 @app.post('/admin/api/bookings/{ref}/reschedule')
 async def admin_reschedule(ref:str,req:Request):
  try:auth(req,True)
  except BookingError:return safe_error()
  try:b=await req.json();start=_admin_stamp(b['start']);end=_admin_stamp(b['end'])
  except (BookingError,KeyError,TypeError):return JSONResponse({'error':'Invalid time'},400)
  with service.store.connect() as db:r=db.execute("SELECT * FROM appointments WHERE ref=? AND mode='internal'",(ref,)).fetchone()
  if not r:return JSONResponse({'error':'Booking not found'},404)
  slot={'start':start.isoformat().replace('+00:00','Z'),'end':end.isoformat().replace('+00:00','Z'),'duration_minutes':int((end-start).total_seconds()/60)}
  try:data=service.adapter.reschedule_booking(r['uid'],slot);service.store.save_appointment(ref,r['scope'],'internal',r['package'],r['idx'],data)
  except BookingError as e:return JSONResponse({'error':e.code},409)
  return {'success':True,'appointment_id':ref,'start':data['start'],'end':data['end'],'booking_status':'confirmed'}
