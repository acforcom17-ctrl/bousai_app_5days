import json
import os
import unittest

from app import app, shelters, parse_area_warnings


class ShelterRegisterTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.original = os.path.join(os.path.dirname(__file__), 'bousai_app', 'data', 'shelters.json')
        self.original_data = []
        with open(self.original, encoding='utf-8') as f:
            self.original_data = json.load(f)

    def tearDown(self):
        with open(self.original, 'w', encoding='utf-8') as f:
            json.dump(self.original_data, f, ensure_ascii=False, indent=2)
        shelters[:] = self.original_data

    def test_register_shelter_with_post(self):
        with self.client.session_transaction() as session:
            session['logged_in'] = True
            session['username'] = 'admin'

        response = self.client.post('/shelter_register', data={'name': '新しい避難所'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('新しい避難所', response.get_data(as_text=True))

        with open(self.original, encoding='utf-8') as f:
            stored = json.load(f)
        self.assertTrue(any(s.get('name') == '新しい避難所' for s in stored))

    def test_parse_area_warnings_accepts_jma_city_codes(self):
        sample = [{
            'reportDatetime': '2026-09-02T11:17:00+09:00',
            'warning': {
                'class20Items': [{
                    'areaCode': '0220100',
                    'kinds': [{'code': '03', 'status': '継続'}]
                }]
            }
        }]

        warnings, report_datetime = parse_area_warnings(sample)
        self.assertEqual(report_datetime, '2026-09-02T11:17:00+09:00')
        self.assertTrue(any(w['code'] == '03' for w in warnings))


if __name__ == '__main__':
    unittest.main()
