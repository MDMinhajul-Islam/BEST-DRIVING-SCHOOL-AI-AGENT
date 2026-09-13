"""Offline blueprint validation, not Retell execution or server authorization."""
def can_confirm(mode,result,write_enabled=False,customer_verified=False,caller_approved=False):
 if not isinstance(result,dict) or result.get('success') is not True or result.get('booking_confirmed') is not True:return False
 booking=result.get('booking')
 if not isinstance(booking,dict) or not isinstance(booking.get('appointment_id'),str) or not booking['appointment_id']:return False
 if not customer_verified or not caller_approved:return False
 if mode=='demo_mock':return result.get('mode')=='mock' and result.get('synthetic') is True and result.get('production') is False and booking['appointment_id'].startswith('MOCK-')
 if mode=='production_safe':return write_enabled is True and result.get('mode')=='production' and result.get('production') is True and result.get('backend_success_verified') is True and not booking['appointment_id'].startswith('MOCK-')
 return False

def validate_design(design,package_ids):
 nodes=design['nodes'];ids={n['id'] for n in nodes};variables=design['variables'];errors=[]
 if len(ids)!=len(nodes) or ids!=set(f'{i:02}' for i in range(10)):errors.append('Invalid node IDs')
 if len({n['name'] for n in nodes})!=len(nodes):errors.append('Duplicate node names')
 for n in nodes:
  if (set(n['reads'])|set(n['writes']))-variables.keys():errors.append('Undefined node variables')
 for v in variables.values():
  if (set(v['set_by'])|set(v['read_by']))-ids:errors.append('Invalid variable owner/reader')
 for e in design['handoffs']:
  if e['from'] not in ids or e['to'] not in ids or e['to']=='00':errors.append('Invalid handoff')
 scenarios=design['scenarios'];sids={s['id'] for s in scenarios}
 for n in nodes:
  if set(n['tests'])-sids:errors.append('Missing test reference')
 for s in scenarios:
  if s['starting_node'] not in ids or set(s['variables'])-variables.keys():errors.append('Invalid scenario context')
 states=set(design['booking_states'])
 for e in design['booking_state_transitions']:
  if e['from'] not in states or e['to'] not in states:errors.append('Invalid booking state')
  if e['to']=='BOOKING_CONFIRMED' and (e['from']!='BOOKING_PENDING' or 'EXPLICIT_BACKEND_SUCCESS' not in e['guard']):errors.append('Unsafe confirmation path')
 def walk(value):
  if isinstance(value,dict):
   if isinstance(value.get('package_id'),str) and value['package_id'] not in package_ids:errors.append('Unknown package reference')
   if 'available_slots' in value and isinstance(value['available_slots'],list) and value['available_slots']:errors.append('Static availability')
   for child in value.values():walk(child)
  elif isinstance(value,list):
   for child in value:walk(child)
 walk(design)
 return errors
