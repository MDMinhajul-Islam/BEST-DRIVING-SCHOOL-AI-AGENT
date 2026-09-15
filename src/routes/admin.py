"""Authenticated same-application admin dashboard for the internal calendar MVP."""
import os,json,hmac,hashlib,secrets,base64,time,uuid,re
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from fastapi import Request
from fastapi.responses import HTMLResponse,JSONResponse
from src.booking.validators import BookingError,utc_stamp,date_bounds

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

PAGE='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>BDS Calendar Admin</title><style>
:root{font-family:Inter,system-ui;color:#172033;background:#f4f7fb}body{margin:0}.bar{background:#102a43;color:white;padding:18px 5vw;display:flex;justify-content:space-between}.wrap{max-width:1180px;margin:24px auto;padding:0 20px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px}.card,section{background:white;border:1px solid #dce5ef;border-radius:12px;padding:18px;margin-bottom:18px;box-shadow:0 3px 12px #102a4310}.n{font-size:28px;font-weight:750;color:#0b6bcb}h1,h2{margin-top:0}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:10px;border-bottom:1px solid #e8eef5;font-size:14px}.status{padding:3px 8px;border-radius:10px;background:#dff5e8}.cancelled{background:#fee2e2}input,select,button{padding:9px;border:1px solid #b8c7d9;border-radius:7px;margin:3px}button{background:#0b6bcb;color:white;border:0;cursor:pointer}.danger{background:#b42318}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px}.muted{color:#60758a}.login{max-width:380px;margin:12vh auto}</style></head><body><div id="app"></div><script>
const A=document.querySelector('#app');let csrf='';async function api(path,opt={}){opt.headers={'Content-Type':'application/json',...(csrf?{'X-CSRF-Token':csrf}:{}),...(opt.headers||{})};let r=await fetch(path,opt);let j=await r.json();if(r.status===401){login();throw Error('auth')}if(!r.ok)throw Error(j.error||'Request failed');return j}
function login(){A.innerHTML='<section class="login"><h1>Calendar Admin</h1><p class="muted">Authorized staff only</p><input id="u" placeholder="Username"><input id="p" type="password" placeholder="Password"><button onclick="goLogin()">Log in</button><p id="e"></p></section>'}async function goLogin(){try{let j=await api('/admin/api/login',{method:'POST',body:JSON.stringify({username:u.value,password:p.value})});csrf=j.csrf;load()}catch(e){document.querySelector('#e').textContent='Login failed'}}
async function load(){let d=await api('/admin/api/summary');csrf=d.csrf;A.innerHTML=`<div class="bar"><b>Best Driving School · Calendar Admin</b><button onclick="logout()">Logout</button></div><main class="wrap"><div class="cards"><div class="card"><div class="n">${d.today}</div>Today</div><div class="card"><div class="n">${d.upcoming}</div>Upcoming</div><div class="card"><div class="n">${d.active}</div>Active sessions</div><div class="card"><div class="n">${d.cancelled}</div>Cancelled</div><div class="card"><div class="n">${d.rules}</div>Active rules</div></div><section><h2>Availability rules</h2><div class="grid"><input id="pkg" placeholder="Canonical package ID"><select id="wd">${['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].map((x,i)=>`<option value=${i}>${x}</option>`)}</select><input id="st" type="time"><input id="et" type="time"><input id="es" type="date"><input id="ee" type="date"><input id="cap" type="number" min="1" placeholder="Capacity"></div><button onclick="rule()">Create active rule</button><div id="rules"></div></section><section><h2>Blackouts</h2><p class="muted">Times use America/Chicago.</p><div class="grid"><input id="bpkg" placeholder="Package ID or *"><input id="bs" type="datetime-local"><input id="be" type="datetime-local"><input id="bn" placeholder="Optional note"></div><button onclick="blackout()">Add blackout</button><div id="blackouts"></div></section><section><h2>Bookings / calendar</h2><input id="q" placeholder="Search customer or reference"><select id="status"><option value="">All statuses</option><option>accepted</option><option>cancelled</option></select><button onclick="bookings()">Filter</button><div id="bookings"></div></section></main>`;await Promise.all([rules(),blacks(),bookings()])}
async function rule(){await api('/admin/api/availability',{method:'POST',body:JSON.stringify({package_id:pkg.value,weekday:+wd.value,start_time:st.value,end_time:et.value,effective_start:es.value,effective_end:ee.value||null,capacity:+cap.value})});await load()}async function blackout(){await api('/admin/api/blackouts',{method:'POST',body:JSON.stringify({package_id:bpkg.value||'*',start:bs.value,end:be.value,note:bn.value})});await load()}
async function rules(){let d=await api('/admin/api/availability');document.querySelector('#rules').innerHTML=tab(d.items,['package_id','weekday','start_time','end_time','capacity','active'],'rule')}async function blacks(){let d=await api('/admin/api/blackouts');document.querySelector('#blackouts').innerHTML=tab(d.items,['package_id','start','end','note','active'],'blackout')}async function bookings(){let d=await api('/admin/api/bookings?q='+encodeURIComponent(q?.value||'')+'&status='+encodeURIComponent(status?.value||''));document.querySelector('#bookings').innerHTML=tab(d.items,['appointment_ref','customer_name','package_id','start','end','status'],'booking')}
function tab(items,cols,type){return '<table><thead><tr>'+cols.map(x=>'<th>'+x.replaceAll('_',' ')+'</th>').join('')+'<th>Action</th></tr></thead><tbody>'+items.map(x=>'<tr>'+cols.map(c=>`<td>${esc(String(x[c]??''))}</td>`).join('')+`<td>${type==='rule'&&x.active===1?`<button onclick="editRule('${x.id}','${x.start_time}','${x.end_time}',${x.capacity})">Edit</button>`:''}${x.active===1?`<button class="danger" onclick="deact('${type}','${x.id}')">Disable</button>`:''}${type==='booking'?`<button onclick="viewB('${x.appointment_ref}')">Details</button>`:''}${type==='booking'&&x.status==='accepted'?`<button onclick="moveB('${x.appointment_ref}')">Reschedule</button><button class="danger" onclick="cancelB('${x.appointment_ref}')">Cancel</button>`:''}</td></tr>`).join('')+'</tbody></table>'}function esc(x){return x.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function deact(t,id){if(confirm('Disable this item?')){await api('/admin/api/'+(t==='rule'?'availability/':'blackouts/')+id+'/deactivate',{method:'POST',body:'{}'});load()}}async function editRule(id,s,e,c){let ns=prompt('Local start HH:MM',s),ne=prompt('Local end HH:MM',e),nc=prompt('Capacity',c);if(ns&&ne&&nc){await api('/admin/api/availability/'+id,{method:'POST',body:JSON.stringify({start_time:ns,end_time:ne,capacity:+nc})});load()}}async function viewB(ref){let d=await api('/admin/api/bookings/'+ref);alert(JSON.stringify(d,null,2))}async function moveB(ref){let s=prompt('New UTC start, ISO 8601'),e=prompt('New UTC end, ISO 8601');if(s&&e){await api('/admin/api/bookings/'+ref+'/reschedule',{method:'POST',body:JSON.stringify({start:s,end:e})});load()}}async function cancelB(ref){if(confirm('Cancel this session? This does not issue a refund.')){await api('/admin/api/bookings/'+ref+'/cancel',{method:'POST',body:'{}'});load()}}async function logout(){await api('/admin/api/logout',{method:'POST',body:'{}'});csrf='';login()}load().catch(()=>login())
</script></body></html>'''

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
   vals={'today':db.execute("SELECT count(*) FROM internal_sessions WHERE status='accepted' AND start>=? AND start<?",(day_start.isoformat().replace('+00:00','Z'),day_end.isoformat().replace('+00:00','Z'))).fetchone()[0],'upcoming':db.execute("SELECT count(*) FROM internal_sessions WHERE status='accepted' AND start>=?",(datetime.now(timezone.utc).isoformat(),)).fetchone()[0],'active':db.execute("SELECT count(*) FROM internal_sessions WHERE status='accepted'").fetchone()[0],'cancelled':db.execute("SELECT count(*) FROM internal_sessions WHERE status='cancelled'").fetchone()[0],'rules':db.execute("SELECT count(*) FROM availability_rules WHERE active=1").fetchone()[0]}
  return vals|{'csrf':s['csrf'],'timezone':'America/Chicago'}
 @app.get('/admin/api/bookings')
 def bookings(req:Request,q:str='',status:str=''):
  try:auth(req)
  except BookingError:return safe_error()
  if len(q)>100 or status not in ('','accepted','cancelled'):return JSONResponse({'error':'Invalid filter'},400)
  sql='SELECT s.*,g.customer_name,g.customer_email,g.scope FROM internal_sessions s JOIN booking_groups g ON g.id=s.group_id WHERE 1=1';args=[]
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
   if pid!='*' and not db.execute('SELECT 1 FROM internal_services WHERE package_id=? AND auto_schedulable=1',(pid,)).fetchone():return JSONResponse({'error':'Unsupported package'},400)
   db.execute('INSERT INTO availability_rules VALUES(?,?,?,?,?,?,?,?,?,?,?)',(rid,pid,wd,start,end,es,ee,cap,1,at,at));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'availability_created','availability_rule',rid,json.dumps({'package_id':pid,'capacity':cap})))
  return {'success':True,'id':rid}
 @app.post('/admin/api/availability/{rid}/deactivate')
 def disable_rule(rid:str,req:Request):
  try:auth(req,True)
  except BookingError:return safe_error()
  at=datetime.now(timezone.utc).isoformat()
  with service.store.connect() as db:db.execute('UPDATE availability_rules SET active=0,updated_at=? WHERE id=?',(at,rid));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'availability_disabled','availability_rule',rid,'{}'))
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
   if not db.execute('SELECT 1 FROM availability_rules WHERE id=?',(rid,)).fetchone():return JSONResponse({'error':'Rule not found'},404)
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
  if end<=start or not isinstance(pid,str) or len(pid)>100 or not isinstance(note,str) or len(note)>300:return JSONResponse({'error':'Invalid blackout'},400)
  bid='BO-'+uuid.uuid4().hex;at=datetime.now(timezone.utc).isoformat()
  with service.store.connect() as db:db.execute('INSERT INTO blackouts VALUES(?,?,?,?,?,?,?)',(bid,pid,start.isoformat().replace('+00:00','Z'),end.isoformat().replace('+00:00','Z'),note,1,at));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'blackout_created','blackout',bid,json.dumps({'package_id':pid})))
  return {'success':True,'id':bid}
 @app.post('/admin/api/blackouts/{bid}/deactivate')
 def disable_blackout(bid:str,req:Request):
  try:auth(req,True)
  except BookingError:return safe_error()
  at=datetime.now(timezone.utc).isoformat()
  with service.store.connect() as db:db.execute('UPDATE blackouts SET active=0 WHERE id=?',(bid,));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'blackout_disabled','blackout',bid,'{}'))
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
  try:b=await req.json();start=utc_stamp(b['start']);end=utc_stamp(b['end'])
  except (BookingError,KeyError,TypeError):return JSONResponse({'error':'Invalid time'},400)
  with service.store.connect() as db:r=db.execute("SELECT * FROM appointments WHERE ref=? AND mode='internal'",(ref,)).fetchone()
  if not r:return JSONResponse({'error':'Booking not found'},404)
  slot={'start':start.isoformat().replace('+00:00','Z'),'end':end.isoformat().replace('+00:00','Z'),'duration_minutes':int((end-start).total_seconds()/60)}
  try:data=service.adapter.reschedule_booking(r['uid'],slot);service.store.save_appointment(ref,r['scope'],'internal',r['package'],r['idx'],data)
  except BookingError as e:return JSONResponse({'error':e.code},409)
  return {'success':True,'appointment_id':ref,'start':data['start'],'end':data['end'],'booking_status':'confirmed'}
