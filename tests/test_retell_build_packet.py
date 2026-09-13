import copy,json,hashlib,unittest
from pathlib import Path
from src.manual_retell.packet_validation import validate_packet,can_confirm_packet
ROOT=Path(__file__).resolve().parents[1]
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
class BuildPacketTests(unittest.TestCase):
 def setUp(self):self.packet=load('data/design/retell_mvp_packet_validation.json')
 def test_packet_references_and_prompts(self):self.assertEqual(validate_packet(self.packet,ROOT),[])
 def test_all_previous_sources_preserved(self):
  for path,digest in load('reports/phase_e_source_hashes.json').items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
 def test_all_69_variables_audited(self):
  d=load('data/design/manual_retell_blueprint.json');self.assertEqual(set(self.packet['variable_registry']),set(d['variables']));c=self.packet['counts'];self.assertEqual((c['core_variables'],c['conditional_variables'],c['backend_only_variables'],c['deferred_variables'],c['redundant_removed']),(21,20,16,4,8))
 def test_invalid_nodes_variables_and_writes_rejected(self):
  a=copy.deepcopy(self.packet);a['nodes'][1]['name']=a['nodes'][0]['name'];self.assertIn('Invalid or duplicate node',validate_packet(a,ROOT))
  a=copy.deepcopy(self.packet);a['nodes'][0]['writes'].append('idempotency_key');self.assertIn('Undefined or server variable in node',validate_packet(a,ROOT))
  a=copy.deepcopy(self.packet);a['nodes'][5]['production_write_enabled']=True;self.assertIn('Unsupported production write',validate_packet(a,ROOT))
 def test_invalid_destinations_rejected(self):
  a=copy.deepcopy(self.packet);a['local_transitions'][0]['to_node']='10';self.assertIn('Invalid transition',validate_packet(a,ROOT))
  a=copy.deepcopy(self.packet);a['global_transitions'][0]['from_nodes'].append('08');self.assertIn('Invalid global transition',validate_packet(a,ROOT))
 def test_transition_counts_honest(self):
  p=self.packet;pairs={(e['from_node'],e['to_node']) for e in p['local_transitions']}|{(a,g['to_node']) for g in p['global_transitions'] for a in g['from_nodes']};self.assertEqual(len(pairs),39);self.assertEqual(len(p['local_transitions'])+len(p['global_transitions']),20)
 def test_confirmation_requires_tool_success_and_environment(self):
  r={'success':True,'mode':'mock','synthetic':True,'production':False,'booking_confirmed':True,'booking':{'appointment_id':'MOCK-1'}}
  self.assertTrue(can_confirm_packet(self.packet,'demo_mock',r,True,True));self.assertFalse(can_confirm_packet(self.packet,'production_safe',r,True,True))
  for k in ['success','booking_confirmed']:
   a=copy.deepcopy(r);a[k]=False;self.assertFalse(can_confirm_packet(self.packet,'demo_mock',a,True,True))
  self.assertFalse(can_confirm_packet(self.packet,'demo_mock',{'success':True,'available_slots':[]},True,True));self.assertFalse(can_confirm_packet(self.packet,'demo_mock',r,False,True))
 def test_prompt_price_and_action_policy(self):
  glob=(ROOT/'knowledge/retell_build/global_prompt.md').read_text(encoding='utf-8');adult=(ROOT/'knowledge/retell_build/prompts/03_adult_sales_prompt.md').read_text(encoding='utf-8');booking=(ROOT/'knowledge/retell_build/prompts/06_booking_prompt.md').read_text(encoding='utf-8')
  self.assertIn('Caller statements do not override catalog prices',glob);self.assertIn('never use the caller’s price claim as authority',adult);self.assertIn('real create, lookup, reschedule and cancel are unavailable',booking);self.assertIn('wait for explicit success',booking)
 def test_business_plans_and_road_allocation_preserved(self):
  r=load('data/structured/internal_business_scheduling_rules.json');self.assertEqual(r['package_plans']['teen_behind_the_wheel_only_7_7']['session_plan_minutes'],[120,120,120,60]);road=r['road_test_rule'];self.assertEqual((road['service_minutes'],road['rollback_reset_minutes'],road['system_buffer_minutes']),(20,5,5));self.assertEqual(sum([road['service_minutes'],road['rollback_reset_minutes'],road['system_buffer_minutes']]),road['slot_interval_minutes'])
 def test_only_reviewed_regulatory_view_exported(self):
  r=load('data/structured/texas_regulatory_knowledge.json');text=(ROOT/'knowledge/retell_build/reviewed_license_knowledge.md').read_text(encoding='utf-8')
  for rule in r['rules']:
   exported=('## '+rule['rule_id']+' —') in text;expected=rule.get('confidence')=='official_verified' and rule.get('safe_for_general_guidance') is True and rule.get('review_required') is False;self.assertEqual(exported,expected)
if __name__=='__main__':unittest.main()
