"""Offline CTO business-rule reconciliation; no regulatory or Retell mutation."""
import json,copy
from pathlib import Path
from config.settings import ROOT
SOURCE={'source_type':'INTERNAL BUSINESS RULE','authority':'CTO / Best Driving School business confirmation','status':'BUSINESS VERIFIED','rule_source_type':'internal_business_rule','rule_source':'CTO','business_verified':True,'backend_enforcement_verified':False,'confirmation_date':'2026-09-13','source_reference':'User-provided CTO confirmation, attachment 5d548e66-9068-4035-a9aa-ce004437b8d1; not website-derived or regulatory'}
ROAD={'service_type':'road_test','road_test_service_minutes':20,'service_minutes':20,'rollback_reset_minutes':5,'system_buffer_minutes':5,'slot_interval_minutes':30,**SOURCE}
def session_plan(hours):
 if isinstance(hours,bool) or not isinstance(hours,(int,float)) or hours<=0 or hours*60!=int(hours*60):raise ValueError('Positive whole-minute driving hours required')
 minutes=int(hours*60);full,remainder=divmod(minutes,120)
 return {'total_driving_hours':hours,'standard_session_minutes':120,'full_session_count':full,'remaining_minutes':remainder,'total_session_count':full+bool(remainder),'session_plan_minutes':[120]*full+([remainder] if remainder else []),**SOURCE}
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(path,value):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def append(path,body):
 p=ROOT/path;s=p.read_text(encoding='utf-8');marker='## Phase C.1 — CTO business-rule reconciliation'
 s=s.split('\n'+marker)[0];p.write_text(s+'\n'+marker+'\n\n'+body+'\n',encoding='utf-8')
def main():
 names=['session_rules','scheduling_models','package_booking_requirements','course_package_booking_map']
 for name in names:
  archive=ROOT/f'data/operational_evidence/phase_c_original/{name}.json'
  if not archive.exists():save(str(archive.relative_to(ROOT)),read(f'data/structured/{name}.json'))
 sessions=read('data/structured/session_rules.json');plans={};roads={}
 for p in sessions:
  pid=p['package_id'];hours=p['purchased_components']['driving_hours']
  if 'phase_c_frontend_observation' not in p:p['phase_c_frontend_observation']={k:copy.deepcopy(p.get(k)) for k in ['session_duration_minutes','expected_session_count','frontend_block_count','status']}
  p['backend_enforcement_verified']=False
  if hours is not None:
   plans[pid]=session_plan(hours);p.update(plans[pid]);p['derived_driving_session_requirement']=copy.deepcopy(plans[pid])
  else:p['derived_driving_session_requirement']=None;p['business_rule_application_status']='Not applied: purchased instructor driving hours not established; PTDE practice hours and road-test preparation are not converted by name.'
  if pid.startswith('road_test_'):p['road_test_scheduling_requirement']=copy.deepcopy(ROAD);roads[pid]=copy.deepcopy(ROAD)
  p['observation_scheduling_business_verified']=False
 save('data/structured/session_rules.json',sessions)
 for name in ['scheduling_models','package_booking_requirements']:
  a=read(f'data/structured/{name}.json')
  for p in a:
   pid=p['package_id'];p['derived_driving_session_requirement']=plans.get(pid);p['road_test_scheduling_requirement']=roads.get(pid);p['backend_enforcement_verified']=False
  save(f'data/structured/{name}.json',a)
 a=read('data/structured/course_package_booking_map.json')
 for program in a['programs']:
  for course in program['courses']:
   for p in course['packages']:
    pid=p['package_id'];p['derived_driving_session_requirement']=plans.get(pid);p['road_test_scheduling_requirement']=roads.get(pid);p['backend_enforcement_verified']=False
 save('data/structured/course_package_booking_map.json',a)
 save('data/structured/internal_business_scheduling_rules.json',{'driving_lesson_rule':{'standard_session_minutes':120,'remainder_rule':'Final shorter session for remaining purchased driving minutes',**SOURCE},'road_test_rule':ROAD,'scope_exclusions':['Texas regulatory eligibility','observation-hour scheduling','PTDE instructor/practice allocation not established','unknown preparation duration'],'package_plans':plans})
 body='Source type: **INTERNAL BUSINESS RULE**. Authority: **CTO / Best Driving School business confirmation**. Status: **BUSINESS VERIFIED**. These are internal scheduling rules, not DPS/TDLR regulations or scraped facts.\n\nStandard driving lessons are 120 minutes; divide known purchased driving minutes into full sessions plus a final shorter remainder. Five adult packages map to 1–5 sessions. Both teen packages have 7 actual driving hours: `[120,120,120,60]`, four driving sessions. Classroom and observation scheduling remain separate and unverified. PTDE practice-hour labels and road-test preparation do not establish instructor driving hours, so no lesson plan is inferred for them.\n\nRoad tests: 20 minutes service + 5 minutes rollback/reset + 5 minutes system buffer = 30-minute allocation interval. The CTO rule governs intended operational design. Original road frontend observations (15-minute ranges with starts 20 minutes apart) remain preserved; they do not prove backend allocation. Never round, fabricate, or silently reinterpret returned live slots to fit this rule. Validate starts against a confirmed backend schedule origin/resource model; until then, use staff assistance for binding selection.\n\nHistorical frontend session fields/evidence are preserved separately from `derived_driving_session_requirement`. Backend enforcement remains independently unverified for every package. Stable package/slot/location/resource IDs, transaction lifecycle, lookup/reschedule/cancel, customer verification, payment/refund policies, pickup/dropoff and remaining-session accounting are still unresolved. No Retell configuration or production capabilities changed.'
 for path in ['docs/availability_contract.md','docs/retell_booking_tool_contracts.md','knowledge/retell_support/booking_persona_data_requirements.md','knowledge/retell_support/booking_state_reference.md','reports/phase_c_booking_investigation.md','reports/booking_gap_analysis.md']:append(path,body)
 p=ROOT/'reports/phase_c1_business_rule_update.md';p.write_text('# Phase C.1 business-rule update\n\n'+body+'\n\n## Reconciliation coverage\n\nSeven driving package plans derived (five adult, two teen); two road-test packages receive the service allocation model. Three PTDE plans remain unassigned and online education has no timed lesson plan. Original four structured files archived under `data/operational_evidence/phase_c_original/`; original website evidence and regulatory files preserved.\n\nRebuild safely: `python -m src.manual_retell.business_rules` after any Phase C regeneration. This command is offline and idempotent.\n',encoding='utf-8')
 print('Business rules reconciled: 7 driving plans; 2 road-test models; backend enforcement unverified.')
if __name__=='__main__':main()
