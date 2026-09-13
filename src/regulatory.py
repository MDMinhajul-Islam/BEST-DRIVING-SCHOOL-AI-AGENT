"""Reproducible, offline Phase B assembly from preserved official evidence.

Research/curation is explicit in config/regulatory_rules.json. This is not a
general legal inference engine, eligibility decision or Retell workflow.
"""
import copy
import json
import re
from collections import Counter
from datetime import date, timedelta
from config.settings import ROOT
from src.regulatory_collect import official_url, normalized_sections
from src.utils import digest, tidy, write_json, write_text

RESEARCH_DATE = '2026-09-13'
LABELS = {'official_verified','official_but_date_uncertain','conflicting_official_sources',
          'business_only','requires_human_review','requires_dps_confirmation'}
CATEGORIES = ['adult_first_time','teen','learner_license','parent_taught','driver_education',
              'road_test','impact_texas_drivers','new_texas_resident','international_driver',
              'documents','third_party_testing','exceptions']
DATES = {'TX-DPS-001':'2024-11-25','TX-DPS-002':'2024-02-27','TX-DPS-004':'2020-09-28',
         'TX-DPS-005':'2020-09-22','TX-DPS-007':'2020-09-22','TX-DPS-008':'2020-09-22',
         'TX-DPS-017':'2025-01-03','TX-DPS-P01':'2026-03','TX-DPS-P02':'2025-10',
         'TX-TDLR-P03':'2025-12'}
DOCUMENTS = {
 'TX-R012':['High-school diploma/GED or valid VOE'],
 'TX-R013':['Applicable learner-stage education certificate','Identity','Texas residency','Citizenship/lawful presence','SSN as applicable','Parent/guardian or accepted waiver/notarized application'],
 'TX-R019':['TDLR instructor designation','Supplied PTDE program guide'],
 'TX-R032':['Printed ITD completion certificate within 90 days'],
 'TX-R034':['Application','Identity','Texas residency','Citizenship/lawful presence','SSN as applicable','Owned-vehicle insurance or no-vehicle statement','Owned-vehicle registration for new-resident out-of-state exchange'],
 'TX-R035':['One primary OR two secondary OR one secondary plus two supporting identity documents','Legal name-change evidence if applicable'],
 'TX-R036':['Two printed named Texas-address residency documents, subject to DPS exceptions'],
 'TX-R040':['Applicant-category lawful-presence evidence'],
 'TX-R041':['Current registration','Current insurance without applicant exclusion'],
 'TX-R042':['Valid identification'],
 'TX-R044':['Applicable completed education evidence','ITD evidence','Third-party test results via confirmed accepted handoff'],
 'TX-R047':['Existing license for surrender','Applicable Texas application documents']}
CERTIFICATES = {'TX-R001':['Adult education completion evidence (ADE-1317 for adult six-hour course)'],
 'TX-R013':['DE-964/DEE-964/DE-964E as applicable'],
 'TX-R016':['Completed classroom/in-car education evidence','ITTD within 90 days'],
 'TX-R032':['ITD completion certificate within 90 days'],
 'TX-R044':['Completed classroom/in-car education evidence','ITD']}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def canonical(text):
    return re.sub(r'[^a-z0-9]+',' ',text.lower()).strip()


def change_status(previous_hash, current_hash, redirects=False, removed=False):
    if removed:
        return 'SOURCE_REMOVED'
    if redirects:
        return 'SOURCE_REDIRECTED'
    return 'UNCHANGED' if previous_hash == current_hash else 'CHANGED' if previous_hash else 'NEW'


def registry(review_current=False):
    inventory=read_json(ROOT/'config/regulatory_source_map.json')
    path=ROOT/'data/structured/regulatory_sources.json'
    old={s['source_id']:s for s in read_json(path)} if path.exists() else {}
    result=[]
    for entry in inventory:
        sid=entry['source_id']; previous=old.get(sid,{})
        record={**previous,**entry,'source_type':'pdf' if entry['url'].lower().endswith('.pdf') else 'webpage',
                'reviewed':False,'last_verified':None,'review_required':True,
                'recommended_recheck':RESEARCH_DATE,'reviewed_content_hash':None}
        raw_html=ROOT/f'data/regulatory_sources/html/{sid}.html'
        raw_pdf=ROOT/f'data/regulatory_sources/pdfs/{sid}.pdf'
        web=ROOT/f'data/regulatory_sources/extracted/{sid}.web.json'
        extracted=ROOT/f'data/regulatory_sources/extracted/{sid}.txt'
        method=None; text=''; raw=None; web_text=None
        if raw_html.exists():
            raw=raw_html
            title,text,headings,dates,links=normalized_sections(raw.read_bytes(),entry['url'])
            record.update(title=title,headings=headings,displayed_dates=dates)
            method='original_html'
        elif raw_pdf.exists() and extracted.exists():
            raw=raw_pdf; text=extracted.read_text(encoding='utf-8');method='original_pdf'
        elif web.exists():
            web_text=read_json(web)
            if isinstance(web_text,str) and len(web_text)>500 and 'Total lines:' in web_text and not web_text.startswith('Internal Error'):
                # Preserve the original tool response separately; line/page locators
                # remain in that archive. No HTML/PDF is fabricated from it.
                text='\n'.join(re.sub(r'^L\d+(?:@P[\d-]+)?:\s*','',line)
                               for line in web_text.splitlines() if re.match(r'^L\d+',line))
                text=re.sub(r'cite[^†]*†([^]*)',r'\1',text)
                record['title']=web_text.splitlines()[0].split(' (https://')[0].strip(' "') or sid
                record['web_snapshot_path']=web.relative_to(ROOT).as_posix()
                method='web_tool_extract'
                record['notes']='Actual source opened and relevant sections read with web tool; original bytes unavailable due direct network timeout. Tool extract is preserved, not a raw HTML/PDF archive.'
                match=re.search(r'Redirected to URL: (https://[^;\s]+)',web_text)
                if match:
                    record['web_redirect_observed']=match.group(1)
        if text and len(text)>100:
            write_text(extracted,text)
            current=digest(tidy(text)); old_hash=previous.get('normalized_content_hash')
            method_changed=previous.get('preservation_method') not in (None,method)
            changed_since_review=bool(previous.get('reviewed_content_hash') and previous['reviewed_content_hash']!=current)
            refresh_failed=bool(previous.get('reviewed_content_hash') and not previous.get('reviewed')
                                and previous.get('change_status') in ('FETCH_FAILED','SOURCE_REMOVED'))
            approved=(not changed_since_review and not refresh_failed) or review_current
            record.update(active=not refresh_failed,reviewed=approved,last_verified=RESEARCH_DATE if approved else previous.get('last_verified'),
                          retrieved_at=previous.get('retrieved_at') or RESEARCH_DATE,
                          preservation_method=method,original_archived=bool(raw),
                          raw_path=raw.relative_to(ROOT).as_posix() if raw else None,
                          extracted_path=extracted.relative_to(ROOT).as_posix(),
                          content_hash=digest(raw.read_bytes()) if raw else digest(web_text),
                          previous_normalized_hash=old_hash,normalized_content_hash=current,
                          reviewed_content_hash=current if approved else previous.get('reviewed_content_hash'),review_required=not approved,
                          normalization_version='phase-b-1',preservation_method_changed=method_changed,
                          change_status=previous.get('change_status') if refresh_failed else change_status(old_hash,current,bool(record.get('redirects') or record.get('web_redirect_observed'))),
                          published_or_updated=DATES.get(sid),date_type='revision' if sid in ('TX-DPS-P01','TX-DPS-P02','TX-TDLR-P03') else 'displayed_page_date' if sid in DATES else None,
                          currency_status='official_verified' if sid in DATES else 'official_but_date_uncertain',
                          recommended_recheck=(date.fromisoformat(RESEARCH_DATE)+timedelta(days=90)).isoformat())
            if sid not in DATES:
                record['notes']=(record.get('notes') or '')+' No reliable update/effective date displayed; live retrieval confirms availability, not amendment history.'
            if sid=='TX-TDLR-P03':
                record['notes']='Rev. Dec. 2025; body uses 24 hours but embedded historical curriculum cover says 32. Overview age wording includes 25, unlike precise DPS age 25+ exemption. Do not use those ambiguous overview statements.'
            if sid=='TX-TDLR-P01':
                record['notes']='No revision date displayed; relevant steps corroborated against current TDLR webpages. Public step-sheet, not the complete program guide delivered after designation.'
        else:
            record.update(active=False,reviewed=False,original_archived=False,preservation_method=None,
                          currency_status='requires_human_review',extracted_path=None,raw_path=None,
                          title=record.get('title') or entry['url'].rsplit('/',1)[-1],
                          change_status=record.get('change_status','FETCH_FAILED'))
            record['notes']=record.get('notes') or 'No readable public evidence retrieved; not reviewed and not used as verified authority.'
        result.append(record)
        write_json(ROOT/f'data/regulatory_sources/metadata/{sid}.json',record)
    write_json(path,result)
    return result


def build_rules(sources):
    lookup={s['source_id']:s for s in sources}; rules=[]
    for item in read_json(ROOT/'config/regulatory_rules.json'):
        rule=copy.deepcopy(item); evidence=[]
        for sid,anchor in item['sources']:
            source=lookup[sid]
            text=(ROOT/source['extracted_path']).read_text(encoding='utf-8') if source.get('extracted_path') else ''
            if canonical(anchor) not in canonical(text):
                raise ValueError(f'{item["rule_id"]}: evidence anchor absent: {sid}: {anchor}')
            evidence.append({'source_id':sid,'url':source['url'],'section_locator':anchor,
                             'extracted_path':source['extracted_path'],
                             'normalized_content_hash':source['normalized_content_hash']})
        rule.pop('sources')
        confidence=item.get('confidence','official_verified')
        rule.update(confidence=confidence,official_sources=list(dict.fromkeys(e['source_id'] for e in evidence)),
                    evidence=evidence,last_verified=RESEARCH_DATE,
                    source_last_updated={sid:lookup[sid]['published_or_updated'] for sid in set(e['source_id'] for e in evidence)},
                    review_required=confidence!='official_verified',
                    exceptions=None,required_documents=DOCUMENTS.get(item['rule_id']),required_certificates=CERTIFICATES.get(item['rule_id']),
                    safe_for_general_guidance=confidence=='official_verified',
                    review_status='reviewed_general_guidance' if confidence=='official_verified' else 'blocked_pending_confirmation')
        rules.append(rule)
    return {'schema_version':'1.0','research_date':RESEARCH_DATE,'jurisdiction':'Texas',
            'scope':'General noncommercial Class C licensing guidance; not an individualized eligibility determination.',
            'categories':CATEGORIES,'rules':rules,
            'terminology':{'official_term':'Learner License','caller_aliases':['permit','learner permit','instruction permit'],
                           'aliases_are_input_recognition_only':True,
                           'distinctions':{'driver_education':'Approved instruction and completion certificate',
                                           'practice':'Supervised driving experience and logs',
                                           'road_test':'Driving skills assessment',
                                           'license':'DPS-issued driving credential subject to its restrictions'}},
            'unresolved_questions':unresolved()}


def unresolved():
    return [
      {'id':'TX-U01','topic':'Teen classroom/block/hybrid totals','status':'CONFLICT','rule_ids':['TX-R006','TX-R008','TX-R026'],'action':'Ask TDLR/provider which current approved curriculum applies; review 24/32 wording.'},
      {'id':'TX-U02','topic':'PTDE daily instruction limits','status':'CONFLICT','rule_ids':['TX-R025'],'action':'TDLR must clarify combined classroom/in-car daily credit; do not calculate timeline.'},
      {'id':'TX-U03','topic':'Adult restricted license and TPST eligibility','status':'REQUIRES HUMAN REVIEW','rule_ids':['TX-R045','TX-R055'],'action':'Retrieve TPST page/DL-65 and confirm current school authorization and applicant prerequisites.'},
      {'id':'TX-U04','topic':'Adult with teen certificate ITD program','status':'CONFLICT','rule_ids':['TX-R033'],'action':'DPS/provider must confirm acceptable program.'},
      {'id':'TX-U05','topic':'Minor out-of-state transfer stage','status':'CONFLICT','rule_ids':['TX-R049'],'action':'DPS must resolve equivalent-license versus learner-six-month guidance.'},
      {'id':'TX-U06','topic':'Test-vehicle annual inspection paperwork','status':'CONFLICT','rule_ids':['TX-R043'],'action':'DPS/provider must clarify DL-60 wording; distinguish examiner safety check from annual inspection.'},
      {'id':'TX-U07','topic':'Foreign/visitor/IDP and unusual documents','status':'REQUIRES DPS CONFIRMATION','rule_ids':['TX-R037','TX-R039','TX-R048','TX-R050','TX-R052','TX-R054'],'action':'Individual country/status/document or exemption determination belongs to DPS. IDP-specific authority not found.'},
      {'id':'TX-U08','topic':'PTDE instructor full screening','status':'REQUIRES HUMAN REVIEW','rule_ids':['TX-R022'],'action':'Public questionnaire preserved without submission; verify actual instructor with TDLR/DPS. Complete designated program guide was not obtained.'},
      {'id':'TX-U09','topic':'Teen restriction expiry and result handoff','status':'REQUIRES DPS CONFIRMATION','rule_ids':['TX-R044','TX-R056'],'action':'Confirm exact restriction durations and authorized digital versus sealed-envelope submission.'}]


PATH_SPECS = [
 ('teen_first_time','First-time teen','REVIEW',['TX-R005','TX-R006','TX-R007','TX-R013','TX-R009','TX-R010','TX-R014','TX-R015','TX-R016','TX-R017','TX-R018']),
 ('adult_first_time_18_24','First-time adult ages 18–24','READY',['TX-R001','TX-R003','TX-R034','TX-R030','TX-R031','TX-R032','TX-R004']),
 ('adult_first_time_25_plus','First-time adult ages 25+','READY',['TX-R002','TX-R003','TX-R034','TX-R030','TX-R031','TX-R032','TX-R004']),
 ('adult_with_learner_license','Adult with learner/restricted license','REVIEW',['TX-R055','TX-R001','TX-R002','TX-R030','TX-R032','TX-R045']),
 ('teen_with_learner_license','Teen with learner license','REVIEW',['TX-R010','TX-R014','TX-R015','TX-R016','TX-R006']),
 ('parent_taught_student','Parent-taught student','REVIEW',['TX-R021','TX-R022','TX-R023','TX-R019','TX-R020','TX-R007','TX-R008','TX-R024','TX-R014','TX-R015','TX-R025','TX-R016']),
 ('road_test_ready','Road-test readiness assessment','REVIEW',['TX-R016','TX-R030','TX-R032','TX-R041','TX-R042','TX-R043','TX-R045','TX-R004']),
 ('new_texas_resident','New Texas resident','REVIEW',['TX-R046','TX-R034','TX-R036','TX-R047','TX-R048','TX-R049','TX-R050']),
 ('out_of_state_transfer','Adult valid US-state license exchange','READY',['TX-R046','TX-R047','TX-R034','TX-R036']),
 ('foreign_license_holder','Foreign license holder','REVIEW',['TX-R050','TX-R051','TX-R052','TX-R040','TX-R034']),
 ('uncertain_or_exception','Exception or uncertain applicant','REVIEW',['TX-R037','TX-R039','TX-R048','TX-R053','TX-R054','TX-R056'])]


def build_pathways(knowledge,mappings):
    lookup={r['rule_id']:r for r in knowledge['rules']};result=[]
    for pid,name,status,ids in PATH_SPECS:
        rules=[lookup[i] for i in ids]
        result.append({'pathway_id':pid,'caller_situation':name,'status':status,
            'readiness_scope':'General pathway explanation only; READY does not authorize booking, establish individual eligibility or certify a particular provider.',
            'required_inputs':['age','first_license','current_license_type','texas_residency_status',
                               'driver_education_status','learner_license_status','parent_taught_status','road_test_goal',
                               'license_issuing_jurisdiction','license_expiry','impact_program','impact_certificate_date'],
            'conditions':({'age_min':18,'age_max':24,'first_license':True} if pid=='adult_first_time_18_24' else
                          {'age_min':25,'first_license':True} if pid=='adult_first_time_25_plus' else
                          {'age_min':18,'valid_unexpired_us_out_of_state_license':True,'surrender_license':True} if pid=='out_of_state_transfer' else
                          {'selection':'Match caller status; clarify before choosing this pathway.'}),
            'rule_ids':ids,'verified_steps':[{'order':i+1,'rule_id':r['rule_id'],'conditions':r['conditions'],'requirements':r['requirements']} for i,r in enumerate(rules) if r['safe_for_general_guidance']],
            'blocked_rule_ids':[r['rule_id'] for r in rules if r['review_required']],
            'possible_school_services':[m['mapping_id'] for m in mappings if set(m['rule_ids'])&set(ids)],
            'official_sources':sorted(set(s for r in rules for s in r['official_sources'])),
            'unknown_inputs_block_individual_qualification':True})
    return {'schema_version':'1.0','research_date':RESEARCH_DATE,'pathways':result}


def build_service_map(kb,knowledge):
    lookup={r['rule_id']:r for r in knowledge['rules']};result=[]
    for course in kb['courses']:
        category=course['category']
        ids={'adult':['TX-R002'],'teen':['TX-R014','TX-R006'],
             'parent_taught':['TX-R015','TX-R019'],'road_test':['TX-R004','TX-R045']}.get(category,['TX-R027'])
        label=(course['course_name']+' '+course['name']).lower()
        if category=='adult' and ('online' in label or 'education' in label):
            ids=['TX-R001','TX-R027'];need='Possible approved adult education option; verify current approval and completion certificate.'
        elif category=='adult':
            need='Optional driving skill preparation; does not by itself replace education, ITD or testing.'
        elif category=='teen':
            need='Possible classroom/in-car education component; separately account for observation, supervised practice and holding period.'
        elif category=='parent_taught':
            need='Possible practice/log support; confirm authorized supervisor, accepted hours and course documentation. Package alone is not PTDE authorization.'
        else:
            need='Possible skills test or test preparation; confirm provider authorization, applicant prerequisites and DPS result handoff.'
        result.append({'mapping_id':'TX-M-'+course['id'],'caller_situation':category,
                       'regulatory_need':need,'rule_ids':ids,
                       'possible_school_service':{'course_id':course['id'],'course_name':course['course_name'],'package_name':course['name']},
                       'match_confidence':'likely','relationship_status':'potential_match',
                       'official_sources':sorted(set(s for rid in ids for s in lookup[rid]['official_sources'])),
                       'business_sources':course['sources'],
                       'review_required':True,'reason':'Phase A proves the advertised offering, not current government approval or acceptance for an individual applicant.',
                       'state_requires_this_school_package':False})
    return result


def validate(knowledge,sources,pathways,mappings):
    from jsonschema import Draft202012Validator, FormatChecker
    schema=read_json(ROOT/'config/texas_regulatory_knowledge.schema.json')
    schema_errors=list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(knowledge))
    errors=[];by_source={s['source_id']:s for s in sources};rules=knowledge['rules']; ids=[r['rule_id'] for r in rules]; rule_set=set(ids)
    errors.extend('Schema: '+e.message for e in schema_errors)
    if len(ids)!=len(rule_set):errors.append('Duplicate rule IDs')
    if len(by_source)!=len(sources):errors.append('Duplicate source IDs')
    if set(knowledge['categories'])!=set(CATEGORIES):errors.append('Required categories missing')
    for source in sources:
        if not official_url(source['url']):errors.append('Non-government registry URL: '+source['source_id'])
        if source['authority_level'] not in (1,2,3,4):errors.append('Invalid authority level')
    for rule in rules:
        if not isinstance(rule.get('conditions'),dict) or not rule.get('requirements'):errors.append('Invalid conditional rule '+rule['rule_id'])
        if rule.get('confidence') not in LABELS:errors.append('Invalid confidence label')
        if not rule.get('official_sources') or not rule.get('evidence'):errors.append('Unattributed rule '+rule['rule_id'])
        if rule.get('review_required') != (rule.get('confidence')!='official_verified'):errors.append('Review gate mismatch')
        if rule.get('safe_for_general_guidance') != (rule.get('confidence')=='official_verified'):errors.append('Guidance gate mismatch')
        if {e.get('source_id') for e in rule.get('evidence',[])}!=set(rule.get('official_sources',[])):errors.append('Evidence/source attribution mismatch')
        for sid in rule.get('official_sources',[]):
            s=by_source.get(sid)
            if not s or not s.get('reviewed') or not s.get('active') or not official_url(s['url']):errors.append('Unavailable/non-authoritative source '+sid)
        for e in rule.get('evidence',[]):
            s=by_source.get(e.get('source_id'))
            if not s or e.get('normalized_content_hash')!=s.get('normalized_content_hash'):errors.append('Evidence hash mismatch')
            elif not s.get('extracted_path') or not (ROOT/s['extracted_path']).exists():errors.append('Evidence file missing')
            elif canonical(e.get('section_locator','')) not in canonical((ROOT/s['extracted_path']).read_text(encoding='utf-8')):errors.append('Evidence locator missing')
    map_ids={m['mapping_id'] for m in mappings}
    for p in pathways['pathways']:
        if not set(p['rule_ids'])<=rule_set or not set(p['official_sources'])<=set(by_source):errors.append('Invalid pathway references')
        if not set(p['possible_school_services'])<=map_ids:errors.append('Invalid pathway services')
        if p['status']=='READY' and p['blocked_rule_ids']:errors.append('READY pathway includes blocked rules')
    course_ids={c['id'] for c in read_json(ROOT/'data/structured/courses.json')}
    for m in mappings:
        if m['possible_school_service']['course_id'] not in course_ids or not m['business_sources']:errors.append('Unsupported business mapping')
        if m['state_requires_this_school_package']:errors.append('Business package misrepresented as law')
    return errors


def append_section(path,heading,content):
    text=path.read_text(encoding='utf-8') if path.exists() else ''
    marker='\n## '+heading+'\n'
    text=text.split(marker)[0].rstrip()+marker+'\n'+content+'\n'
    write_text(path,text)


def conflict_records(kb):
    historical={c['field']:c for c in kb['conflicts'] if 'field' in c}
    return [
      {'issue':'adult_education_applicability','classification':'POSSIBLE REGULATORY CONFLICT',
       'school_website_statement':historical.get('adult_education_applicability',{}).get('values',[]),
       'official_statement':'DPS requires education for first-time ages 18–24 and explicitly exempts ages 25+. Valid adult out-of-state exchanges have a waiver.',
       'official_source':['TX-DPS-001','TX-TDLR-001'],'resolution':'Regulatory age scope resolved; flag broad all-adults school wording for owner correction. Preserve historical source evidence.','status':'resolved'},
      {'issue':'platform_age_policy_vs_teen_services','classification':'BUSINESS POLICY',
       'school_website_statement':historical.get('platform_age_policy_vs_teen_services',{}).get('values',[]),
       'official_statement':'TDLR supports teen education from 14 and learner issuance from 15; this does not decide website account/guardian enrollment policy.',
       'official_source':['TX-TDLR-001','TX-DPS-002'],'resolution':'Owner must clarify guardian enrollment and platform terms; government licensing evidence cannot resolve a school account policy.','status':'human_review'},
      {'issue':'school_teen_classroom_hours','classification':'REQUIRES HUMAN REVIEW',
       'school_website_statement':[{'value':c.get('classroom_hours'),'sources':c['sources']} for c in kb['courses'] if c['category']=='teen'],
       'official_statement':'Official pages contain 24/32-hour discrepancies. Preserve school course duration and confirm approved curriculum; do not assume the advertised duration is legally obsolete.',
       'official_source':['TX-TDLR-001','TX-TDLR-005','TX-TDLR-008'],'resolution':'TDLR/provider curriculum confirmation required.','status':'human_review'},
      {'issue':'school_digital_test_results_vs_DL68','classification':'WORDING DIFFERENCE',
       'school_website_statement':[x for x in kb['licensing_guidance'] if 'portal' in x.get('content','').lower() or 'upload' in x.get('content','').lower()],
       'official_statement':'DL-68 describes sealed-envelope results; the school advertises a DPS submission process. Confirm current authorized digital submission rather than declaring either invalid.',
       'official_source':['TX-DPS-P02'],'resolution':'Confirm provider-specific result handoff with instructor.','status':'human_review'},
      {'issue':'practice_packages_vs_full_education','classification':'NO CONFLICT',
       'school_website_statement':[{'course_id':c['id'],'description':c.get('description'),'sources':c['sources']} for c in kb['courses'] if c['category']=='parent_taught'],
       'official_statement':'Practice, classroom, observation and skills assessment are distinct components.',
       'official_source':['TX-TDLR-002','TX-TDLR-006'],'resolution':'Keep service component mapping conditional; avoid claiming a practice package satisfies the full state pathway.','status':'resolved'}]


TOPICS=[('Adult first-time license','VERIFIED','adult_first_time'),('Teen pathway','CONFLICT','teen'),
        ('Driver education','CONFLICT','driver_education'),('Learner license','PARTIAL','learner_license'),
        ('Parent-taught','CONFLICT','parent_taught'),('Road-test eligibility','PARTIAL','road_test'),
        ('Road-test documents','PARTIAL','road_test'),('Impact Texas Drivers','PARTIAL','impact_texas_drivers'),
        ('Third-party skills test','PARTIAL','third_party_testing'),('New Texas resident','PARTIAL','new_texas_resident'),
        ('Out-of-state transfer','PARTIAL','new_texas_resident'),('International driver','REQUIRES DPS CONFIRMATION','international_driver'),
        ('Required documents','PARTIAL','documents'),('Exceptions','REQUIRES DPS CONFIRMATION','exceptions')]


def render(knowledge,sources,pathways,mappings,conflicts):
    folder=ROOT/'knowledge/regulatory';lookup={s['source_id']:s for s in sources}
    header=f'Regulatory research date: {RESEARCH_DATE}\n\nGeneral Class C guidance. Use only records marked `official_verified` for general answers; flagged details require confirmation. Source dates are not assumed effective dates.\n\n'
    def links(ids):return ', '.join(f'[{sid}]({lookup[sid]["url"]})' for sid in ids)
    filenames={'adult_first_time':'adult_first_time_license','teen':'teen_license_pathway','learner_license':'learner_license',
               'parent_taught':'parent_taught_driver_education','driver_education':'driver_education_requirements','road_test':'road_test_requirements',
               'impact_texas_drivers':'impact_texas_drivers','new_texas_resident':'new_texas_residents','international_driver':'international_drivers',
               'documents':'required_documents','third_party_testing':'third_party_testing','exceptions':'exceptions_and_edge_cases'}
    for category,name in filenames.items():
        text='# '+name.replace('_',' ').title()+'\n\n'+header
        for r in knowledge['rules']:
            if r['category']!=category:continue
            text+=f'## {r["rule_id"]}: {r["title"]}\n\nApplies when: `{json.dumps(r["conditions"],ensure_ascii=False)}`\n\n'+ '\n'.join('- '+s for s in r['requirements'])+'\n\n'
            text+=f'Confidence: `{r["confidence"]}`. Review required: {r["review_required"]}.\n\nSources: '+links(r['official_sources'])+'\n\n'
        if category=='documents':
            text+='## Conditional checklist\n\nAll applicants: identity, residency, citizenship/lawful status, SSN as applicable and application (R034–R040). Teen learner: education milestone, guardian/waiver and diploma/GED/VOE (R012–R013). Teen provisional: completed education, learner and ITD evidence (R016/R044). Skills test: identification, valid ITD and vehicle documents as applicable (R032/R041–R043). Exchange applicants: existing license, surrender choice and owned-vehicle registration (R034/R047). Confirm original document acceptance with DPS; do not accept caller claims as verified documents.\n'
        if category=='learner_license':text+='\nOfficial term: **Learner License**. Caller aliases: permit, learner permit, instruction permit. These aliases help recognize intent; they do not establish an equivalent credential or extend teen rules to adults.\n'
        write_text(folder/(name+'.md'),text)
    write_text(folder/'README.md','# Official Texas regulatory knowledge\n\n'+header+'Separate structured layer: `data/structured/texas_regulatory_knowledge.json`. The master business file contains an additive `regulatory_reference`; existing school evidence remains business-only.\n\nRebuild offline: `.venv/Scripts/python.exe -m src.regulatory`. Refresh public originals: `python -m src.regulatory_collect`, then review changed sources and curate rules before rebuilding. A refresh does not approve changed rules automatically. Review [unresolved questions](unresolved_questions.md) and [manual review](../../reports/phase_b_manual_review.md).\n\nREADY pathways support general explanation only. Adult permits, provider-specific TPST admission, foreign licensing and flagged details are not approved for automatic qualification or booking. Retell remains manually configured later.\n')
    text='# Regulatory source index\n\n'+header+'| Source | Agency | Type | Reviewed | Original archived | Source date | Preservation |\n| --- | --- | --- | --- | --- | --- | --- |\n'
    for s in sources:text+=f'| [{s["source_id"]}]({s["url"]}) | {s["agency"]} | {s["source_type"]} | {s["reviewed"]} | {s["original_archived"]} | {s.get("published_or_updated") or "Not displayed"} | {s.get("preservation_method") or "Unavailable"} |\n'
    write_text(folder/'source_index.md',text)
    text='# Unresolved regulatory questions\n\n'+header
    for u in knowledge['unresolved_questions']:text+=f'## {u["id"]}: {u["topic"]}\n\n{u["status"]}. {u["action"]}\n\nRules: '+', '.join(u['rule_ids'])+'\n\n'
    text+='Not reviewed: complete DL-7 handbook, DL-65, full purchased/designated PTDE guide, and inaccessible DPS scheduling/TPST/provisional pages. The removed TDLR old one-sheet URL is not a current authority. No independent IDP-specific rule was found.\n'
    write_text(folder/'unresolved_questions.md',text)
    reports=ROOT/'reports'
    text='# Regulatory coverage\n\n'+header+'| Topic | Status | Primary authority | Sources | Notes |\n| --- | --- | --- | --- | --- |\n'
    for title,status,category in TOPICS:
        rs=[r for r in knowledge['rules'] if r['category']==category]; ids=sorted(set(s for r in rs for s in r['official_sources']))
        notes='Usual general pathway verified; individual approval remains DPS.' if status=='VERIFIED' else '; '.join(r['title'] for r in rs if r['review_required']) or 'Conditional documents and special cases require confirmation.'
        text+=f'| {title} | {status} | DPS / TDLR | {links(ids)} | {notes} |\n'
    write_text(reports/'regulatory_coverage.md',text)
    text='# Regulatory conflicts\n\n'+header+'Historical Phase A evidence is unchanged. Official disagreements are blocked rather than resolved by source age or rank alone.\n\n'
    for c in conflicts:
        text+=f'## {c["issue"]} — {c["classification"]}\n\nSchool evidence: see the corresponding structured `school_website_statement` with preserved business sources in `reports/regulatory_conflicts.json`.\n\nOfficial statement: {c["official_statement"]}\n\nAssessment/action: {c["resolution"]}\n\nStatus: {c["status"]}. Sources: {links(c["official_source"])}\n\n'
    text+='## Official-source conflicts\n\n'
    for u in knowledge['unresolved_questions']:
        if u['status']=='CONFLICT':text+=f'- {u["id"]}: **{u["topic"]}** — {u["action"]} Rules: '+', '.join(u['rule_ids'])+'\n'
    text+='\nOther official ambiguities: SSN affidavit prerequisites, provider result handoff and precise restriction expiry. The Dec. 2025 TDLR overview uses age “14 and 25,” while DPS explicitly says no education at 25+; use precise DPS scope for the adult explanation and retain the overview discrepancy for review. No business source has been marked regulatory authority.\n'
    write_text(reports/'regulatory_conflicts.md',text)
    write_json(reports/'regulatory_conflicts.json',conflicts)
    text='# Regulatory freshness\n\n'+header+'A current public page may have an old publication date. No hidden amendment date is invented. `official_but_date_uncertain` sources have no reliable update date; corroborated individual rules may still be `official_verified`. Recheck before production, every 90 days thereafter, immediately on changed content, and at the earliest known effective-date boundary.\n\n| Source | Agency | Topic | Last verified | Source date | Potential stale information | Recheck | Change |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n'
    for s in sources:text+=f'| {s["source_id"]} | {s["agency"]} | {", ".join(s["topics"])} | {s.get("last_verified") or "Not reviewed"} | {s.get("published_or_updated") or "Unknown"} | {s["currency_status"]}; {"original unavailable" if not s["original_archived"] else "original saved"} | {s["recommended_recheck"]} | {s["change_status"]} |\n'
    text+='\nOffline rebuild verifies archived hashes and evidence anchors, not remote currency. Collector reports NEW/UNCHANGED/CHANGED/SOURCE_REMOVED/SOURCE_REDIRECTED/FETCH_FAILED; failed retrieval is not proof of removal. A normalization/preservation-method change must be distinguished from a regulatory amendment. CHANGED sources require manual review of all dependent rules.\n'
    write_text(reports/'regulatory_freshness_report.md',text)
    reviewed=[s for s in sources if s['reviewed']];counts=Counter((s['agency'],s['source_type']) for s in reviewed)
    stats={'dps_pages':counts['Texas DPS','webpage'],'tdlr_pages':counts['Texas TDLR','webpage'],
           'pdfs':sum(s['source_type']=='pdf' for s in reviewed),'original_pdfs':sum(s['source_type']=='pdf' and s['original_archived'] for s in reviewed),
           'rules':len(knowledge['rules']),'verified_rules':sum(not r['review_required'] for r in knowledge['rules']),
           'review_rules':sum(r['review_required'] for r in knowledge['rules']),
           'verified_topics':sum(s=='VERIFIED' for _,s,_ in TOPICS),'partial_topics':sum(s=='PARTIAL' for _,s,_ in TOPICS),
           'unresolved_topics':sum(s not in ('VERIFIED','PARTIAL') for _,s,_ in TOPICS),
           'business_regulatory_conflicts':sum(c['classification']=='POSSIBLE REGULATORY CONFLICT' for c in conflicts),
           'official_source_conflicts':sum(u['status']=='CONFLICT' for u in knowledge['unresolved_questions'])}
    write_json(reports/'regulatory_summary.json',stats)
    quality='# Regulatory quality report\n\n'+header+'\n'.join(f'- {k.replace("_"," ")}: {v}' for k,v in stats.items())+'\n\n'
    quality+='Topics fully covered: usual adult first-time general pathway. Partial/conflict topics: see the fourteen-row [coverage matrix](regulatory_coverage.md). Not found: IDP-specific guidance; unavailable sources are recorded in the source index, never counted reviewed.\n\nReview gates: all 13 school package relationships remain potential matches; official school approval was not independently verified. Business differences: one adult applicability conflict, guardian account policy, course-hour review and result-handoff wording. Five official conflict clusters plus other documented ambiguities require review. Stale/currency risks: old displayed DPS publication dates, undated TDLR pages and older/removed PDFs; see freshness report.\n\n'
    testing=ROOT/'reports/regulatory_test_results.json'
    if testing.exists():
        t=read_json(testing)
        quality+=f'Tests: existing {t["existing_passed"]}/9 passed; new {t["new_passed"]}/{t["new_total"]} passed; failures {t["failures"]}.\n\n'
    quality+='Testing evidence: `reports/regulatory_test_results.txt` and `regulatory_validation.json`. No production readiness is inferred from tests alone.\n'
    write_text(reports/'regulatory_quality_report.md',quality)
    manual='# Phase B manual review\n\nRegulatory research date: '+RESEARCH_DATE+'\n\nThe additive evidence layer is complete for review: '+str(stats['rules'])+' conditional rules and 11 pathways. Usual adult guidance is ready for general explanation. Teen/PTDE details, provider-specific test gates and foreign/exception cases remain blocked. '+str(stats['official_source_conflicts'])+' official conflict clusters are retained. No Retell workflow or booking backend was changed.\n\n'
    manual+='## Verified\n\nFirst-time ages 18–24 need approved education; DPS exempts ages 25+. Teen education can start at 14 and learner licensing at 15. Standard teen hold is six months unless turning 18, with supervised driving, instruction/observation/practice distinctions. ITD precedes skills testing and has a 90-day certificate window. DPS issues the license after requirements are satisfied. Core documents are conditional, not universal. See individually sourced rules.\n\n'
    manual+='## Business alignment\n\nThe advertised six-hour adult education, adult lessons, teen full/driving-only courses, PTDE practice support and test/preparation packages correspond to different components. All 13 mappings are `potential_match`/`likely`; the public school advertisement does not prove current provider approval or guarantee acceptance. Pricing and package observations remain in Phase A.\n\n'
    manual+='## Conflicts\n\nThe broad all-adults education wording is inconsistent with the DPS 25+ exemption; owner correction is needed. Teen service eligibility does not resolve adult-only website terms. Official 24/32-hour, PTDE daily-credit, adult ITD selection, minor transfer and inspection-paperwork disagreements are documented in [conflicts](regulatory_conflicts.md).\n\n'
    manual+='## Uncertain\n\nDPS direct downloads timed out. Reviewed DPS pages/PDFs have tool extracts, not archived original bytes. TPST page/DL-65, full DL-7 and designated PTDE guide were not reviewed. Foreign/SSN/affidavit/expiry/military cases require individual confirmation. No complete-scope claim is made.\n\n'
    manual+='## Human decisions needed\n\n1. TDLR/instructor: approved classroom hours and daily PTDE limits.\n2. Owner/instructor: current education/testing approvals, adult restricted-license admission and DPS result handoff.\n3. Owner: guardian enrollment terms and broad adult-course wording.\n4. DPS/provider: flagged transfer, ITD selection, inspection paperwork and exception cases.\n\n'
    manual+='## Retell-ready\n\nTexas License Guide: general `official_verified` facts after owner review. Adult Sales: education at 18–24 versus optional lessons at 25+. Teen Sales: age/stage distinctions and instruction versus practice; suppress disputed totals. Road Test Sales: preparation, certificate currency and testing-versus-issuance distinction; provider-specific admission is blocked. Support documents are references for later manual setup. READY never guarantees individual eligibility or live availability.\n\n'
    manual+='## Do not use yet\n\nAny `review_required` rule, definitive foreign recognition/IDP advice, exact PTDE completion timelines, automatic minor-transfer classification, adult TPST qualification or claims that a school package legally satisfies a full pathway. Recheck dated snapshots before production. Recommended next phase: owner/instructor regulatory review and source-gap closure, then manual Retell design using only approved records.\n'
    write_text(reports/'phase_b_manual_review.md',manual)
    render_retell(pathways)
    return stats


def render_retell(pathways):
    folder=ROOT/'knowledge/retell_support'
    questions=[('age','How old is the person getting the license?','Age changes education and license stage.','TX-R001/TX-R002/TX-R005'),
      ('student_or_parent','Are you calling for yourself or for your child?','Identify the student without mistaking caller age for student age.','TX-R013/TX-R019'),
      ('first_license/current_license_type','Is this your first license, or do you already have a license or learner license?','Separate first-time, learner and transfer paths.','TX-R003/TX-R010/TX-R047'),
      ('texas_residency_status','Do you live in Texas now, and did you recently move here?','Separate resident exchange from visitor recognition.','TX-R046/TX-R052'),
      ('license_issuing_jurisdiction/license_expiry','Where was your current license issued, and is it still valid?','Ask only for transfer/foreign callers; expiry and jurisdiction affect waivers.','TX-R047–TX-R052'),
      ('driver_education_status','Have you completed driver education, and which certificate do you have?','Distinguish partial/full adult or teen completion.','TX-R001/TX-R013/TX-R028'),
      ('learner_license_status/issue_date','Do you have a Texas learner license, and when was it issued?','Ask dates when teen holding period matters; account for suspensions.','TX-R010/TX-R055'),
      ('parent_taught_status','Are you using parent-taught education with a designated instructor?','Ask only for PTDE interest/status; authorization is separate from a practice package.','TX-R019–TX-R024'),
      ('road_test_goal','Are you looking for education, driving practice or the driving test?','Route to the relevant component.','TX-R004/TX-R014'),
      ('impact_program/impact_certificate_date','Have you completed Impact Texas Drivers, and when was the certificate issued?','Ask when skills testing is the goal; determine program and 90-day currency.','TX-R030–TX-R033')]
    text='# Licensing qualification questions\n\nManual design reference. Ask only unanswered questions that change this caller’s pathway. Caller statements are self-reported, not verified government records.\n\n'
    for variable,q,why,basis in questions:text+=f'## `{variable}`\n\nQuestion: “{q}”\n\nWhy needed: {why}\n\nSource basis: {basis}, with official references in the structured rule records.\n\n'
    text+='At the testing stage, ask whether teen education, observation/practice logs, required hold, ITD and documents are complete. Do not ask for SSNs or immigration-document numbers in qualification conversation. Refer uncertain document categories to DPS.\n'
    write_text(folder/'licensing_qualification_questions.md',text)
    text='# Texas License Guide reference\n\nRegulatory research date: '+RESEARCH_DATE+'\n\nInternal reference for manual node design; not a final prompt or workflow import.\n\n## What we need to know from the caller\n\nAge of student, first/existing license, exact credential and jurisdiction, residency/move date, education/certificate status, learner issue date when relevant, PTDE designation and testing goal. For tests, establish ITD program/date and unresolved prerequisites. Reuse known answers.\n\n## Possible pathways and rules\n\n| Pathway | General guidance readiness | Rule IDs |\n| --- | --- | --- |\n'
    for p in pathways['pathways']:text+=f'| {p["pathway_id"]} | {p["status"]} | {", ".join(p["rule_ids"])} |\n'
    text+='\n## Manual routing reference\n\nAdult Sales: adult education or optional in-car learning needs; do not force education at 25+. Teen Sales: teen education/driving/PTDE component needs. Road Test Sales: skills testing or preparation after clarification; no automatic eligibility guarantee. Booking: only after the reviewed prerequisites and selected service are established; actual availability/actions require a later backend. Human support: disputed rules, provider authorization, unusual documents, transfer/foreign exceptions or caller contradictions.\n\n## Clarification and no-guess cases\n\nUnclear age/student identity, “permit” without exact credential, expired or foreign licenses, partial teen education at 18, adult teen-certificate ITD selection, incomplete PTDE authorization or logs, and uncertain document acceptance. See regulatory unresolved questions. Use only `official_verified` records; blocking a disputed detail does not prevent explaining other supported steps.\n'
    write_text(folder/'texas_license_guide_reference.md',text)
    text='# Regulatory response guardrails\n\nUse current reviewed official rule records and the actual applicant conditions. Use Learner License as the official teen term. Distinguish classroom education, in-car instruction, practice, skills testing and DPS issuance. Explain usual pathways naturally, clarify contradictory age/status information, and refer unusual cases to DPS/TDLR. Never invent exemptions, documents or eligibility; never present a school policy/package as Texas law. Check source freshness and suppress all `review_required` details pending confirmation. Caller input alone cannot verify license status, certificates, provider approval or documents.\n\n| Unsafe | Corrected pattern |\n| --- | --- |\n| You definitely qualify. | This appears to be the usual pathway from what you’ve shared. DPS makes the final licensing decision. |\n| Every adult must buy our six-hour course. | DPS requires education for first-time applicants 18–24; at 25+ it is not mandatory. Driving lessons may still help. |\n| Our test gives you your license. | A passed skills test satisfies a testing step; DPS still issues your license. |\n| A 15-year-old can take the road test now. | At 15, the usual stage is a learner license. Standard provisional eligibility starts at 16 after the required education, hold and ITTD. |\n| Your foreign license means no testing. | The rules depend on country, validity, residency and surrender choice. Let’s confirm the relevant DPS pathway. |\n| This PTDE package replaces the program guide and all training. | Practice support is one component; designation, approved education and required training/logs remain separate. |\n| Your appointment is booked. | Booking requires a confirmed backend result; static knowledge cannot establish a slot. |\n\nDo not promise exact PTDE completion times, conflicting classroom totals, acceptable adult ITD alternatives, automatic minor transfer eligibility or inspection paperwork from the disputed records.\n'
    write_text(folder/'regulatory_response_guardrails.md',text)
    append_section(folder/'recommended_shared_variables.md','Phase B proposed updates',
      'Manual proposal only. Existing `age`, `student_or_parent`, `license_status` and `permit_status` remain; prefer exact credential normalization rather than duplicate conflicting fields.\n\n| Variable | Status | Purpose |\n| --- | --- | --- |\n| first_time_applicant | RECOMMENDED | Distinguish first-time from exchange |\n| texas_resident_status / move_date | RECOMMENDED | Resident versus visitor and deadline |\n| license_issuing_jurisdiction / license_expiry | RECOMMENDED | Conditional exchange/foreign screening |\n| driver_education_status / certificate_type | RECOMMENDED | Partial/full and adult/teen distinction |\n| learner_license_status / issue_date | RECOMMENDED | Exact credential and teen hold; normalize existing permit_status |\n| parent_taught_status | RECOMMENDED | Designation, selected course and instruction stage |\n| impact_texas_status / program / certificate_date | RECOMMENDED | Correct program and 90-day window |\n| road_test_eligibility | RECOMMENDED | unknown, prerequisites_reported, needs_review; never government-approved |\n| required_document_status | OPTIONAL | Category-level missing/uncertain checklist |\n| suspension_during_hold | OPTIONAL | Ask only if teen holding period matters |\n| foreign_license_status / out_of_state_license_status | NOT NEEDED | Derive from exact license status/jurisdiction rather than duplicate booleans |\n| SSN / document_numbers / criminal_history_details | NOT NEEDED | Refer sensitive eligibility verification to official channels |')
    append_section(folder/'knowledge_source_map.md','Phase B authority separation',
      '| Fact/action category | Source of truth |\n| --- | --- |\n| BUSINESS FACT | Best Driving School public website and reviewed Phase A observations |\n| REGULATORY FACT | Current reviewed Texas DPS / TDLR official records; Phase B rule IDs and evidence |\n| LIVE AVAILABILITY | Approved scheduling API, later integration |\n| BOOKING ACTION | Confirmed booking backend result, later integration |\n| STUDENT-SPECIFIC INFORMATION | Authenticated student system, later integration |\n\nThe earlier Phase A “not collected” regulatory row is a historical baseline; this Phase B section supersedes its readiness statement. School guidance remains historical business evidence and is not elevated to law. The master `regulatory_reference` points to the separate official layer. Proposed service relationships remain conditional.')


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review-current',action='store_true',help='Explicit curator acknowledgement after reviewing changed source content and updating rules; never use as an unattended refresh.')
    args=parser.parse_args()
    sources=registry(args.review_current);knowledge=build_rules(sources)
    kb=read_json(ROOT/'data/structured/knowledge_base.json')
    mappings=build_service_map(kb,knowledge);pathways=build_pathways(knowledge,mappings)
    errors=validate(knowledge,sources,pathways,mappings)
    write_json(ROOT/'reports/regulatory_validation.json',{'research_date':RESEARCH_DATE,'errors':errors,'valid':not errors})
    if errors:raise ValueError('\n'.join(errors))
    write_json(ROOT/'data/structured/texas_regulatory_knowledge.json',knowledge)
    write_json(ROOT/'data/structured/license_pathways.json',pathways)
    write_json(ROOT/'data/structured/regulation_to_service_map.json',mappings)
    kb['regulatory_reference']={'schema_version':'1.0','research_date':RESEARCH_DATE,
        'knowledge':'data/structured/texas_regulatory_knowledge.json','sources':'data/structured/regulatory_sources.json',
        'pathways':'data/structured/license_pathways.json','service_map':'data/structured/regulation_to_service_map.json',
        'business_licensing_guidance_is_not_official_authority':True,'manual_review_required_before_production':True}
    write_json(ROOT/'data/structured/knowledge_base.json',kb)
    stats=render(knowledge,sources,pathways,mappings,conflict_records(kb))
    print(json.dumps(stats,indent=2))


if __name__=='__main__':main()
