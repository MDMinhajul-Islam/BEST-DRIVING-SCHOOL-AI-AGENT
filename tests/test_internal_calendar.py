import unittest,tempfile,json,os
from pathlib import Path
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from src.booking.store import Store
from src.booking.internal_adapter import InternalBookingAdapter
from src.booking.service import BookingService
from src.booking.validators import BookingError,package_plan
from src.routes.booking import create_app
from src.routes.admin import make_password_hash

SCOPE='INTERNAL-TEST-SCOPE-0001';ROAD='road_test_road_test_only';ADULT='adult_4_hours';TEEN='teen_behind_the_wheel_only_7_7'
CUSTOMER={'name':'Test Student','email':'test@example.invalid'}

class InternalCalendarTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'db.sqlite3';self.store=Store(self.path);self.adapter=InternalBookingAdapter(self.store);self.service=BookingService(self.adapter,self.store)
 def rule(self,pid=ROAD,date='2035-10-01',start='09:00',end='17:00',capacity=1):
  from datetime import date as D,datetime,timezone
  day=D.fromisoformat(date);now=datetime.now(timezone.utc).isoformat()
  with self.store.connect() as db:db.execute('INSERT INTO availability_rules VALUES(?,?,?,?,?,?,?,?,?,?,?)',('r'+str(self.store.path)+pid+date+start,pid,day.weekday(),start,end,date,date,capacity,1,now,now))
 def slots(self,pid=ROAD,date='2035-10-01',duration=None):return self.service.check_availability(SCOPE,pid,date,session_duration_minutes=duration)['slots']
 def create(self,pid=ROAD,refs=None):return self.service.create_booking(SCOPE,pid,refs or [self.slots(pid)[0]['slot_ref']],CUSTOMER)
 def test_empty_by_default(self):self.assertEqual(self.slots(),[])
 def test_internal_catalog_and_unresolved(self):
  with self.store.connect() as db:
   self.assertEqual(db.execute("SELECT auto_schedulable FROM internal_services WHERE package_id='road_test_practice_session_road_test'").fetchone()[0],0)
   self.assertEqual(db.execute("SELECT count(*) FROM internal_services").fetchone()[0],13)
 def test_slot_generation(self):
  self.rule();s=self.slots();self.assertEqual(len(s),16);self.assertEqual(s[0]['duration_minutes'],30);self.assertEqual(s[0]['timezone'],'America/Chicago')
 def test_blackout_removes_slots(self):
  self.rule();before=len(self.slots());
  with self.store.connect() as db:db.execute("INSERT INTO blackouts VALUES('b','*','2035-10-01T14:00:00Z','2035-10-01T15:00:00Z','test',1,'x')")
  self.assertEqual(len(self.slots()),before-2)
 def test_capacity_and_release_on_cancel(self):
  self.rule(capacity=1);b=self.create();self.assertTrue(b['booking_confirmed']);self.assertEqual(len(self.slots()),15);self.assertFalse(self.service.cancel_booking(SCOPE,b['appointment_id'])['booking_confirmed']);self.assertEqual(len(self.slots()),16)
 def test_capacity_two(self):
  self.rule(capacity=2);slot=self.slots()[0];a=self.service.create_booking(SCOPE,ROAD,[slot['slot_ref']],CUSTOMER);other='INTERNAL-TEST-SCOPE-0002';slot2=self.service.check_availability(other,ROAD,'2035-10-01')['slots'][0];b=self.service.create_booking(other,ROAD,[slot2['slot_ref']],{'name':'Other Student','email':'other@example.invalid'});self.assertTrue(a['booking_confirmed'] and b['booking_confirmed']);self.assertEqual(len(self.slots()),15)
 def test_double_booking_transaction(self):
  self.rule();ref=self.slots()[0]['slot_ref']
  with ThreadPoolExecutor(2) as pool:out=list(pool.map(lambda i:self.service.create_booking(SCOPE+str(i),ROAD,[self.service.check_availability(SCOPE+str(i),ROAD,'2035-10-01')['slots'][0]['slot_ref'],],{'name':'Student '+str(i),'email':f's{i}@example.invalid'}),range(2)))
  self.assertEqual(sum(x['booking_confirmed'] for x in out),1)
 def test_multi_session_atomic(self):
  self.rule(ADULT);refs=[s['slot_ref'] for s in self.slots(ADULT)[:2]];b=self.create(ADULT,refs);self.assertTrue(b['booking_confirmed']);self.assertEqual(len(b['sessions']),2);self.assertTrue(b['booking_group_id'].startswith('IG-'))
  with self.store.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM internal_sessions').fetchone()[0],2)
 def test_multi_session_conflict_rolls_back(self):
  self.rule(ADULT);refs=[s['slot_ref'] for s in self.slots(ADULT)[:2]]
  with self.store.connect() as db:db.execute("INSERT INTO blackouts VALUES('b','*',?,?,NULL,1,'x')",(self._slot(refs[1])['start'],self._slot(refs[1])['end']))
  out=self.service.create_booking(SCOPE,ADULT,refs,CUSTOMER);self.assertFalse(out['success'])
  with self.store.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM internal_sessions').fetchone()[0],0);self.assertEqual(db.execute('SELECT count(*) FROM booking_groups').fetchone()[0],0)
 def _slot(self,ref):
  with self.store.connect() as db:return dict(db.execute('SELECT * FROM slots WHERE ref=?',(ref,)).fetchone())
 def test_teen_plan(self):self.assertEqual(package_plan(TEEN),[120,120,120,60])
 def test_adult_plans(self):
  for h in [2,4,6,8,10]:self.assertEqual(package_plan(f'adult_{h}_hours'),[120]*(h//2))
 def test_road_plan_and_unresolved(self):
  self.assertEqual(package_plan(ROAD),[30])
  with self.assertRaises(BookingError):package_plan('road_test_practice_session_road_test')
 def test_reschedule_releases_old_and_history(self):
  self.rule();b=self.create();old=b['start'];self.rule(ROAD,'2035-10-02');new=self.slots(ROAD,'2035-10-02')[0];r=self.service.reschedule_booking(SCOPE,b['appointment_id'],new['slot_ref']);self.assertNotEqual(old,r['start']);self.assertTrue(any(x['start']==old for x in self.slots()))
  with self.store.connect() as db:self.assertEqual(db.execute("SELECT count(*) FROM internal_history WHERE action='session_rescheduled'").fetchone()[0],1)
 def test_find_and_persistence(self):
  self.rule();b=self.create();new=BookingService(InternalBookingAdapter(Store(self.path)),Store(self.path));self.assertTrue(new.find_booking(SCOPE,b['appointment_id'])['booking_confirmed'])
 def test_idempotent_create(self):
  self.rule();ref=self.slots()[0]['slot_ref'];a=self.service.create_booking(SCOPE,ROAD,[ref],CUSTOMER);b=self.service.create_booking(SCOPE,ROAD,[ref],CUSTOMER);self.assertEqual(a,b)
  with self.store.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM booking_groups').fetchone()[0],1)
 def test_dst_slots(self):
  self.rule(ROAD,'2035-03-11');self.assertTrue(self.slots(ROAD,'2035-03-11')[0]['start'].endswith('Z'))
 def admin_client(self):
  env={'ADMIN_USERNAME':'admin','ADMIN_PASSWORD_HASH':make_password_hash('correct horse battery staple'),'ADMIN_SESSION_SECRET':'z'*32,'ADMIN_COOKIE_SECURE':'false'}
  with patch.dict(os.environ,env):return TestClient(create_app(self.service,'s'*32))
 def login(self,c):
  r=c.post('/admin/api/login',json={'username':'admin','password':'correct horse battery staple'});self.assertEqual(r.status_code,200);return r.json()['csrf']
 def test_admin_requires_login(self):
  c=self.admin_client();self.assertEqual(c.get('/admin/api/summary').status_code,401);self.assertEqual(c.post('/admin/api/login',json={'username':'admin','password':'bad'}).status_code,401);self.assertEqual(c.get('/admin').status_code,200)
 def test_admin_rule_blackout_booking_and_cancel(self):
  c=self.admin_client();csrf=self.login(c);H={'X-CSRF-Token':csrf};rule={'package_id':ROAD,'weekday':0,'start_time':'09:00','end_time':'11:00','effective_start':'2035-10-01','effective_end':'2035-12-31','capacity':1}
  services=c.get('/admin/api/services').json()['items'];self.assertEqual(len(services),8);self.assertEqual(next(x for x in services if x['package_id']==ADULT)['session_plan'],[120,120])
  self.assertEqual(c.post('/admin/api/availability',headers=H,json=rule).status_code,200);rules=c.get('/admin/api/availability').json()['items'];self.assertEqual(len(rules),1)
  b=self.create();items=c.get('/admin/api/bookings').json()['items'];self.assertEqual(items[0]['appointment_ref'],b['appointment_id'])
  self.assertEqual(c.post('/admin/api/bookings/'+b['appointment_id']+'/cancel',headers=H,json={}).json()['booking_status'],'cancelled')
  self.assertEqual(c.post('/admin/api/blackouts',headers=H,json={'package_id':'*','start':'2035-10-01T14:00:00Z','end':'2035-10-01T15:00:00Z','note':'Synthetic'}).status_code,200)
  self.assertEqual(len(c.get('/admin/api/blackouts').json()['items']),1)
  summary=c.get('/admin/api/summary').json();self.assertEqual(summary['rules'],1);self.assertEqual(summary['blackouts'],1)
  self.assertEqual(c.get('/admin/api/bookings/'+b['appointment_id']).json()['booking']['group_id'],b['booking_group_id'])
  rid=rules[0]['id'];self.assertEqual(c.post('/admin/api/availability/'+rid,headers=H,json={'start_time':'09:30','end_time':'11:30','capacity':2}).status_code,200)
  self.assertEqual(c.post('/admin/api/availability/'+rid+'/deactivate',headers=H).status_code,200);self.assertEqual(c.post('/admin/api/availability/'+rid+'/activate',headers=H).status_code,200)
  bid=c.get('/admin/api/blackouts').json()['items'][0]['id'];self.assertEqual(c.post('/admin/api/blackouts/'+bid+'/deactivate',headers=H).status_code,200);self.assertEqual(c.post('/admin/api/blackouts/'+bid+'/activate',headers=H).status_code,200)
 def test_admin_local_blackout_and_reschedule(self):
  self.rule();b=self.create();self.rule(ROAD,'2035-10-02');c=self.admin_client();csrf=self.login(c);H={'X-CSRF-Token':csrf}
  moved=c.post('/admin/api/bookings/'+b['appointment_id']+'/reschedule',headers=H,json={'start':'2035-10-02T14:00:00Z','end':'2035-10-02T14:30:00Z'})
  self.assertEqual(moved.status_code,200);self.assertEqual(moved.json()['start'],'2035-10-02T14:00:00Z')
  moved_local=c.post('/admin/api/bookings/'+b['appointment_id']+'/reschedule',headers=H,json={'start':'2035-10-02T10:00','end':'2035-10-02T10:30'})
  self.assertEqual(moved_local.status_code,200);self.assertEqual(moved_local.json()['start'],'2035-10-02T15:00:00Z')
  blackout=c.post('/admin/api/blackouts',headers=H,json={'package_id':'*','start':'2035-10-02T09:30','end':'2035-10-02T10:00','note':'Chicago local'})
  self.assertEqual(blackout.status_code,200)
  with self.store.connect() as db:
   self.assertEqual(db.execute('SELECT start FROM blackouts WHERE id=?',(blackout.json()['id'],)).fetchone()[0],'2035-10-02T14:30:00Z')
   self.assertEqual(db.execute("SELECT count(*) FROM internal_history WHERE action='session_rescheduled'").fetchone()[0],2)
 def test_admin_csrf_and_invalid_capacity(self):
  c=self.admin_client();csrf=self.login(c);self.assertEqual(c.post('/admin/api/availability',json={}).status_code,401);r=c.post('/admin/api/availability',headers={'X-CSRF-Token':csrf},json={'package_id':ROAD,'weekday':0,'start_time':'09:00','end_time':'10:00','effective_start':'2035-10-01','capacity':0});self.assertEqual(r.status_code,400)
  short=c.post('/admin/api/availability',headers={'X-CSRF-Token':csrf},json={'package_id':'adult_2_hours','weekday':0,'start_time':'09:00','end_time':'10:00','effective_start':'2035-10-01','capacity':1});self.assertEqual(short.status_code,400);self.assertIn('120-minute',short.json()['error'])
  self.assertEqual(c.get('/admin/api/services').status_code,200);self.assertEqual(self.admin_client().get('/admin/api/services').status_code,401)
 def test_admin_page_is_labeled_and_structured(self):
  page=self.admin_client().get('/admin').text
  for text in ['Staff portal','Availability','Blackouts','Booking details','System status','Username','Password']:
   self.assertIn(text,page)
  self.assertNotIn('<pre',page.lower())
 def test_internal_mode_config_and_health(self):
  env={'BOOKING_PROVIDER':'internal','BOOKING_MODE':'internal','BOOKING_DB_PATH':str(self.path),'ADMIN_USERNAME':'admin','ADMIN_PASSWORD_HASH':make_password_hash('password long enough'),'ADMIN_SESSION_SECRET':'x'*32,'ADMIN_COOKIE_SECURE':'false'}
  with patch.dict(os.environ,env):c=TestClient(create_app(secret='s'*32));self.assertEqual(c.get('/api/health').json()['provider'],'internal')

if __name__=='__main__':unittest.main()
