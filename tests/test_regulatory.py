import copy
import json
import subprocess
import unittest
from unittest.mock import patch
from config.settings import ROOT
from src.regulatory import read_json, validate, change_status, CATEGORIES, conflict_records, append_section, registry
from src.regulatory_collect import official_url, public_source_url, normalized_sections
from tempfile import TemporaryDirectory
from pathlib import Path


class RegulatoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.knowledge=read_json(ROOT/'data/structured/texas_regulatory_knowledge.json')
        cls.sources=read_json(ROOT/'data/structured/regulatory_sources.json')
        cls.paths=read_json(ROOT/'data/structured/license_pathways.json')
        cls.maps=read_json(ROOT/'data/structured/regulation_to_service_map.json')

    def check(self,k=None,s=None,p=None,m=None):
        return validate(k or self.knowledge,s or self.sources,p or self.paths,m or self.maps)

    def test_schema_and_attributed_archived_evidence(self):
        self.assertEqual(self.check(),[])

    def test_schema_rejects_invalid_requirement_type(self):
        k=copy.deepcopy(self.knowledge);k['rules'][0]['requirements']='unsupported shape'
        self.assertTrue(any('Schema:' in e for e in self.check(k=k)))

    def test_verified_rule_requires_source_and_evidence(self):
        k=copy.deepcopy(self.knowledge);k['rules'][0]['official_sources']=[];k['rules'][0]['evidence']=[]
        self.assertTrue(any('Unattributed' in e for e in self.check(k=k)))

    def test_non_government_source_cannot_be_authoritative(self):
        s=copy.deepcopy(self.sources);s[0]['url']='https://bestdrivingschool.us/'
        self.assertTrue(any('Non-government' in e for e in self.check(s=s)))
        for u in ['http://www.dps.texas.gov/','https://www.dps.texas.gov.attacker.com/',
                  'https://user@www.dps.texas.gov/','https://www.dps.texas.gov:444/',
                  'https://tdlr.texas.gov@evil.com/']:
            self.assertFalse(official_url(u),u)

    def test_registry_categories_and_unique_ids(self):
        self.assertEqual(set(self.knowledge['categories']),set(CATEGORIES))
        self.assertEqual(len({r['rule_id'] for r in self.knowledge['rules']}),len(self.knowledge['rules']))
        k=copy.deepcopy(self.knowledge);k['rules'].append(k['rules'][0])
        self.assertIn('Duplicate rule IDs',self.check(k=k))

    def test_unknown_pathway_reference_rejected(self):
        p=copy.deepcopy(self.paths);p['pathways'][0]['rule_ids'].append('TX-R999')
        self.assertIn('Invalid pathway references',self.check(p=p))

    def test_conflicting_rules_are_blocked(self):
        flagged=[r for r in self.knowledge['rules'] if r['confidence']=='conflicting_official_sources']
        self.assertGreaterEqual(len(flagged),5)
        self.assertTrue(all(r['review_required'] and not r['safe_for_general_guidance'] for r in flagged))
        p=copy.deepcopy(self.paths);p['pathways'][0]['status']='READY'
        self.assertIn('READY pathway includes blocked rules',self.check(p=p))

    def test_evidence_hash_mismatch_rejected(self):
        k=copy.deepcopy(self.knowledge);k['rules'][0]['evidence'][0]['normalized_content_hash']='0'*64
        self.assertIn('Evidence hash mismatch',self.check(k=k))

    def test_change_detection_distinguishes_removal_and_redirect(self):
        self.assertEqual(change_status(None,'a'),'NEW')
        self.assertEqual(change_status('a','a'),'UNCHANGED')
        self.assertEqual(change_status('a','b'),'CHANGED')
        self.assertEqual(change_status('a','b',redirects=True),'SOURCE_REDIRECTED')
        self.assertEqual(change_status('a',None,removed=True),'SOURCE_REMOVED')

    def test_public_information_only_and_questionnaire_labels(self):
        self.assertFalse(public_source_url('https://www.tdlr.texas.gov/descerts/login'))
        self.assertFalse(public_source_url('https://www.tdlr.texas.gov/%64escerts/login'))
        self.assertFalse(public_source_url('https://www.tdlr.texas.gov/ParentTaught/PTSelect.aspx'))
        self.assertFalse(public_source_url('https://impacttexasdrivers.dps.texas.gov/itad/login.aspx'))
        self.assertTrue(public_source_url('https://impacttexasdrivers.dps.texas.gov/itad/FAQ.aspx'))
        _,text,_,_,_=normalized_sections('<html><main><form><p><label>Are you at least 25?</label></p><input value="secret"><select><option>private</option></select></form></main></html>','https://www.tdlr.texas.gov/')
        self.assertIn('Are you at least 25?',text)
        self.assertNotIn('secret',text);self.assertNotIn('private',text)

    def test_phase_a_master_data_preserved(self):
        old=json.loads(subprocess.check_output(['git','show','HEAD:data/structured/knowledge_base.json'],cwd=ROOT))
        current=read_json(ROOT/'data/structured/knowledge_base.json')
        self.assertIn('regulatory_reference',current)
        current.pop('regulatory_reference')
        old.pop('regulatory_reference',None)
        # The later package audit explicitly authorizes additive label fields
        # and an offline regeneration timestamp, without changing old facts.
        def original_fields(value):
            if isinstance(value,dict):
                return {k:original_fields(v) for k,v in value.items() if k not in ('marketing_labels','generated_at')}
            if isinstance(value,list):return [original_fields(v) for v in value]
            return value
        self.assertEqual(original_fields(old),original_fields(current))

    def test_conflict_generation_preserves_historical_issues(self):
        conflicts=conflict_records(read_json(ROOT/'data/structured/knowledge_base.json'))
        by_id={c['issue']:c for c in conflicts}
        self.assertEqual(by_id['adult_education_applicability']['status'],'resolved')
        self.assertEqual(by_id['platform_age_policy_vs_teen_services']['status'],'human_review')
        self.assertTrue((ROOT/'reports/regulatory_conflicts.md').exists())
        self.assertTrue(by_id['adult_education_applicability']['school_website_statement'])

    def test_service_map_never_requires_a_school_package(self):
        self.assertEqual(len(self.maps),13)
        self.assertTrue(all(m['relationship_status']=='potential_match' and not m['state_requires_this_school_package'] and m['business_sources'] for m in self.maps))

    def test_additive_document_update_is_idempotent(self):
        with TemporaryDirectory() as temp:
            path=Path(temp)/'test.md';path.write_text('Phase A preserved\n',encoding='utf-8')
            append_section(path,'Phase B','first');append_section(path,'Phase B','second')
            text=path.read_text(encoding='utf-8')
            self.assertTrue(text.startswith('Phase A preserved'))
            self.assertEqual(text.count('## Phase B'),1)
            self.assertNotIn('first',text);self.assertIn('second',text)

    def test_changed_source_does_not_approve_rules_automatically(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)
            for folder in ['config','data/structured','data/regulatory_sources/html','data/regulatory_sources/extracted','data/regulatory_sources/metadata']:
                (root/folder).mkdir(parents=True,exist_ok=True)
            entry={'source_id':'TX-DPS-001','agency':'Texas DPS','url':'https://www.dps.texas.gov/section/driver-license/apply-texas-driver-license','topics':['adult_first_time'],'authority_level':1}
            (root/'config/regulatory_source_map.json').write_text(json.dumps([entry]),encoding='utf-8')
            (root/'data/regulatory_sources/html/TX-DPS-001.html').write_text('<html><title>New page</title><main>'+('changed legal guidance '*20)+'</main></html>',encoding='utf-8')
            old={**entry,'reviewed':True,'reviewed_content_hash':'0'*64,'normalized_content_hash':'0'*64,'last_verified':'2026-09-01','change_status':'UNCHANGED'}
            (root/'data/structured/regulatory_sources.json').write_text(json.dumps([old]),encoding='utf-8')
            with patch('src.regulatory.ROOT',root):
                s=registry()[0]
            self.assertFalse(s['reviewed']);self.assertTrue(s['review_required'])
            self.assertEqual(s['last_verified'],'2026-09-01');self.assertEqual(s['change_status'],'CHANGED')

    def test_business_renderer_preserves_phase_b_extensions(self):
        from src.renderer import generate_retell_support
        kb=read_json(ROOT/'data/structured/knowledge_base.json')
        with TemporaryDirectory() as temp:
            root=Path(temp);folder=root/'knowledge/retell_support';folder.mkdir(parents=True)
            (folder/'recommended_shared_variables.md').write_text('base\n## Phase B proposed updates\n\nKEEP VARIABLES\n',encoding='utf-8')
            (folder/'knowledge_source_map.md').write_text('base\n## Phase B authority separation\n\nKEEP AUTHORITY\n',encoding='utf-8')
            with patch('src.renderer.ROOT',root):generate_retell_support(kb)
            self.assertIn('KEEP VARIABLES',(folder/'recommended_shared_variables.md').read_text(encoding='utf-8'))
            self.assertIn('KEEP AUTHORITY',(folder/'knowledge_source_map.md').read_text(encoding='utf-8'))


if __name__=='__main__':unittest.main()
