import copy,json,hashlib,unittest
from pathlib import Path
from src.manual_retell.business_rules import session_plan,ROAD
from src.manual_retell.validation import validate_design,can_confirm
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
class ManualRetellTests(unittest.TestCase):
 def setUp(self):
  self.design=load('data/design/manual_retell_blueprint.json');self.ids={p['package_id'] for p in load('data/structured/package_catalog.json')}
 def test_complete_design_references(self):self.assertEqual(validate_design(self.design,self.ids),[])
 def test_invalid_handoff_or_variable_rejected(self):
  a=copy.deepcopy(self.design);a['handoffs'][0]['to']='missing';self.assertIn('Invalid handoff',validate_design(a,self.ids));a=copy.deepcopy(self.design);a['nodes'][1]['reads'].append('undefined');self.assertIn('Undefined node variables',validate_design(a,self.ids))
 def test_session_arithmetic_and_remainder(self):
  self.assertEqual(session_plan(7)['session_plan_minutes'],[120,120,120,60])
  for h in [1,2,4,6,8,10,7,2.5]:
   p=session_plan(h);self.assertEqual(sum(p['session_plan_minutes']),h*60);self.assertEqual(p['total_session_count'],len(p['session_plan_minutes']));self.assertTrue(all(m==120 for m in p['session_plan_minutes'][:-1]));self.assertLessEqual(p['session_plan_minutes'][-1],120)
  for h in [0,-1,True,'7']:
   with self.assertRaises(ValueError):session_plan(h)
 def test_seven_packages_and_ptde_exclusion(self):
  rows=load('data/structured/session_rules.json');self.assertEqual(sum(p.get('derived_driving_session_requirement') is not None for p in rows),7)
  for p in rows:
   self.assertFalse(p['backend_enforcement_verified']);self.assertFalse(p['observation_scheduling_business_verified'])
   if p['package_id'].startswith('parent_taught_'):self.assertIsNone(p['derived_driving_session_requirement'])
   if p.get('derived_driving_session_requirement'):self.assertEqual(p['total_driving_hours'],p['purchased_components']['driving_hours'])
 def test_road_allocation_authority(self):
  self.assertEqual(ROAD['service_minutes']+ROAD['rollback_reset_minutes']+ROAD['system_buffer_minutes'],ROAD['slot_interval_minutes']);self.assertEqual(ROAD['slot_interval_minutes'],30);self.assertEqual(ROAD['rule_source_type'],'internal_business_rule');self.assertEqual(ROAD['authority'],'CTO / Best Driving School business confirmation');self.assertFalse(ROAD['backend_enforcement_verified'])
 def test_frontend_history_retained(self):
  before=load('data/operational_evidence/phase_c_original/session_rules.json');after={p['package_id']:p for p in load('data/structured/session_rules.json')}
  for p in before:
   a=after[p['package_id']];self.assertEqual(a['evidence'],p['evidence']);self.assertEqual(a['phase_c_frontend_observation']['expected_session_count'],p['expected_session_count'])
 def test_package_maps_consistent(self):
  plans={p['package_id']:p['derived_driving_session_requirement'] for p in load('data/structured/session_rules.json')}
  for name in ['scheduling_models','package_booking_requirements']:
   for p in load('data/structured/'+name+'.json'):self.assertIn(p['package_id'],self.ids);self.assertEqual(p['derived_driving_session_requirement'],plans[p['package_id']])
  for program in load('data/structured/course_package_booking_map.json')['programs']:
   for c in program['courses']:
    for p in c['packages']:self.assertEqual(p['derived_driving_session_requirement'],plans[p['package_id']])
 def test_business_not_regulatory(self):
  rules=load('data/structured/internal_business_scheduling_rules.json')
  for r in [rules['driving_lesson_rule'],rules['road_test_rule']]+list(rules['package_plans'].values()):self.assertEqual(r['source_type'],'INTERNAL BUSINESS RULE');self.assertEqual(r['status'],'BUSINESS VERIFIED');self.assertEqual(r['rule_source'],'CTO')
  baseline=load('reports/phase_c_preservation_hashes.json')
  for path,digest in baseline.items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
 def test_no_static_availability(self):
  self.assertNotIn('Static availability',validate_design(self.design,self.ids));a=copy.deepcopy(self.design);a['fixture']={'available_slots':[{'time':'09:00'}]};self.assertIn('Static availability',validate_design(a,self.ids))
 def test_confirmation_paths_guarded(self):
  edges=[e for e in self.design['booking_state_transitions'] if e['to']=='BOOKING_CONFIRMED'];self.assertEqual(len(edges),1);a=copy.deepcopy(self.design);a['booking_state_transitions'].append({'from':'SLOT_SELECTED','to':'BOOKING_CONFIRMED','guard':'Caller selected'});self.assertIn('Unsafe confirmation path',validate_design(a,self.ids))
 def test_environment_and_success_confirmation(self):
  r={'success':True,'booking_confirmed':True,'mode':'mock','synthetic':True,'production':False,'booking':{'appointment_id':'MOCK-BOOKING-1'}}
  self.assertTrue(can_confirm('demo_mock',r,customer_verified=True,caller_approved=True));self.assertFalse(can_confirm('production_safe',r,True,True,True));self.assertFalse(can_confirm('demo_mock',r,customer_verified=False,caller_approved=True))
  p={'success':True,'booking_confirmed':True,'mode':'production','production':True,'backend_success_verified':True,'booking':{'appointment_id':'REAL-1'}}
  self.assertFalse(can_confirm('production_safe',p,False,True,True));self.assertTrue(can_confirm('production_safe',p,True,True,True))
  for field in ['success','booking_confirmed','backend_success_verified']:
   q=copy.deepcopy(p);q[field]=False;self.assertFalse(can_confirm('production_safe',q,True,True,True))
  self.assertFalse(can_confirm('production_safe',{'success':True,'available_slots':[]},True,True,True))
 def test_manual_outputs_exist(self):
  files=['global_agent_rules','shared_state','router_node','texas_license_guide_node','adult_sales_node','teen_sales_node','road_test_sales_node','booking_node','booking_state_machine','student_support_node','human_escalation_node','end_call_node','handoff_matrix','persona_prompt_blueprints','retell_build_checklist','test_matrix']
  for name in files:self.assertTrue((ROOT/'knowledge/retell_manual'/f'{name}.md').is_file())
if __name__=='__main__':unittest.main()
