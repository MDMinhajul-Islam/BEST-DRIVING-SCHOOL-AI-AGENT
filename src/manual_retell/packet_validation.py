"""Static manual-packet checks, not deployed Retell authorization."""
import re
from src.manual_retell.validation import can_confirm
def validate_packet(packet,root):
 errors=[];nodes=packet['nodes'];ids={n['id'] for n in nodes};core=set(packet['core_variables']);conditional=set(packet['conditional_variables']);server=set(packet['backend_variables'])
 if len(ids)!=9 or ids!=set(f'{i:02}' for i in range(1,10)) or len({n['name'] for n in nodes})!=9:errors.append('Invalid or duplicate node')
 if not core<=packet['variable_registry'].keys() or core&server:errors.append('Invalid MVP registry')
 allgroups=[set(v for v,r in packet['variable_registry'].items() if r['group']==g) for g in ['CORE','CONDITIONAL','BACKEND-ONLY','FUTURE','REDUNDANT']]
 if sum(map(len,allgroups))!=69 or len(set.union(*allgroups))!=69:errors.append('Incomplete Phase D audit')
 for n in nodes:
  if (set(n['reads'])|set(n['writes']))-(core|conditional):errors.append('Undefined or server variable in node')
  if n.get('production_write_enabled') is not False:errors.append('Unsupported production write')
  p=root/n['prompt_file']
  if not p.is_file():errors.append('Missing prompt');continue
  text=p.read_text(encoding='utf-8')
  if re.search(r'\b\d{1,2}:\d{2}\b',text):errors.append('Static availability in prompt')
  if re.search(r'(?:I am|I’m|I will now|Hello,? I).*?(?:persona|Booking Specialist|Sales Specialist)',text,re.I):errors.append('Persona announcement')
  if re.search(r'\$\d+',text):errors.append('Permanent price in prompt')
 for e in packet['local_transitions']:
  if e['from_node'] not in ids or e['to_node'] not in ids:errors.append('Invalid transition')
  if set(e['carry'])-(core|conditional):errors.append('Undefined handoff variable')
 for g in packet['global_transitions']:
  if g['to_node'] not in ids or not set(g['from_nodes'])<=ids or g['to_node'] in g['from_nodes']:errors.append('Invalid global transition')
 if packet['capabilities']['production_write'] is not False or packet['capabilities']['production_lookup'] is not False:errors.append('Unsupported production capability')
 if 'Explicit appropriate tool success' not in packet['confirmation_guard']:errors.append('Missing tool-success guard')
 return errors

def can_confirm_packet(packet,mode,result,customer_verified=False,caller_approved=False):
 if mode=='production_safe' and packet['capabilities']['production_write'] is not True:return False
 return can_confirm(mode,result,write_enabled=packet['capabilities']['production_write'],customer_verified=customer_verified,caller_approved=caller_approved)
