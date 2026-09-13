import copy
import unittest
from src.package_audit import load, source_inventory, validate_catalog, amount, build_catalog


class PackageAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=load('data/structured/package_catalog.json')
        cls.booking=load('data/structured/package_booking_requirements.json')
        cls.mapping=load('data/structured/course_package_booking_map.json')
        cls.kb=load('data/structured/knowledge_base.json')

    def test_unique_stable_readable_price_independent_ids(self):
        ids=[p['package_id'] for p in self.catalog]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(all('_' in i for i in ids))
        changed=copy.deepcopy(self.kb)
        for c in changed['courses']:c['price']='$1'
        records,_=build_catalog(changed,source_inventory(changed['source_pages']))
        self.assertEqual(ids,[r['package_id'] for r in records])

    def test_every_package_has_business_source_and_matching_raw_observation(self):
        for p in self.catalog:
            self.assertTrue(p['sources'])
            self.assertTrue(all(s['url'].startswith('https://bestdrivingschool.us/') for s in p['sources']))
            self.assertTrue(any(o['price']==p['current_price'] for o in p['option_observations']))

    def test_prices_are_numeric_and_original_is_separate(self):
        self.assertTrue(all(isinstance(p['current_price'],(int,float)) for p in self.catalog))
        online=next(p for p in self.catalog if p['program_id']=='adult_online')
        self.assertEqual(online['current_price'],19.99);self.assertEqual(online['original_price'],70)
        self.assertEqual(amount('$1,350'),1350)
        with self.assertRaises(ValueError):amount('from $100')

    def test_independent_raw_count_and_cross_page_deduplication(self):
        rows=source_inventory(self.kb['source_pages'])
        self.assertEqual(len(rows),91)
        unique={(r['identity_url'],r['canonical_name']) for r in rows}
        self.assertEqual(len(unique),13)
        self.assertEqual(len(self.catalog),13)

    def test_marketing_labels_separate_from_discounts_and_names(self):
        labeled=[p for p in self.catalog if p['marketing_labels']]
        self.assertEqual(len(labeled),4)
        adult=next(p for p in self.catalog if p['package_id']=='adult_10_hours')
        self.assertEqual(adult['marketing_labels'],['Best selling'])
        self.assertEqual(adult['discount']['amount'],55)
        self.assertTrue(all('Best selling' not in p['package_name'] for p in self.catalog))
        teen=next(p for p in self.catalog if p['package_id']=='teen_24_hr_classroom_driving_package')
        self.assertEqual(teen['marketing_labels'],['Best selling'])

    def test_live_slots_are_absent_and_online_access_is_distinct(self):
        self.assertTrue(all(p['live_slots'] is None for p in self.catalog))
        self.assertEqual(sum(p['requires_live_availability'] for p in self.catalog),12)
        online=next(p for p in self.catalog if p['program_id']=='adult_online')
        self.assertFalse(online['booking_required'])
        self.assertEqual(online['availability_source'],'not_applicable_self_paced')
        bad=copy.deepcopy(self.catalog);bad[0]['live_slots']=['Saturday 10 AM']
        self.assertIn('Live slots in static catalog',validate_catalog(bad,self.booking,self.mapping))

    def test_booking_map_only_references_valid_packages(self):
        self.assertEqual({b['package_id'] for b in self.booking},{p['package_id'] for p in self.catalog})
        bad=copy.deepcopy(self.booking);bad[0]['package_id']='nonexistent'
        self.assertIn('Booking map references mismatch',validate_catalog(self.catalog,bad,self.mapping))

    def test_hierarchy_two_teen_courses_share_one_program(self):
        self.assertEqual(validate_catalog(self.catalog,self.booking,self.mapping),[])
        teen=next(p for p in self.mapping['programs'] if p['program_id']=='teen')
        self.assertEqual(len(teen['courses']),2)
        self.assertEqual(sum(len(c['packages']) for c in teen['courses']),2)
        self.assertEqual(sum(len(p['courses']) for p in self.mapping['programs']),6)

    def test_teen_benchmark_hours_prices_and_entry_stage(self):
        full=next(p for p in self.catalog if p['package_id']=='teen_24_hr_classroom_driving_package')
        btw=next(p for p in self.catalog if 'behind_the_wheel_only' in p['package_id'])
        self.assertEqual(full['current_price'],399);self.assertEqual(btw['current_price'],350)
        self.assertEqual([full['included'][h] for h in ('classroom_hours','driving_hours','observation_hours')],[24,7,7])
        self.assertEqual([btw['included'][h] for h in ('classroom_hours','driving_hours','observation_hours')],[0,7,7])
        self.assertTrue(any('completed classroom' in x.lower() for x in btw['prerequisites']))

    def test_fee_does_not_change_base_price_or_claim_unknown_totals(self):
        full=next(p for p in self.catalog if p['package_id']=='teen_24_hr_classroom_driving_package')
        self.assertEqual(full['current_price'],399)
        self.assertEqual(full['additional_fees'][0]['percentage'],3)
        self.assertEqual(full['included']['pickup_dropoff'],None)
        self.assertNotIn('checkout_total',full)

    def test_conflicting_price_is_blocked_not_chosen(self):
        rows=source_inventory(self.kb['source_pages'])
        first=copy.deepcopy(rows[0]);first['price']=425;rows.append(first)
        catalog,conflicts=build_catalog(self.kb,rows)
        self.assertTrue(conflicts)
        p=next(p for p in catalog if p['package_id']==conflicts[0]['package_id'])
        self.assertIsNone(p['current_price']);self.assertEqual(p['price_status'],'conflict_requires_review')


if __name__=='__main__':unittest.main()
