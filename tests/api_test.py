import unittest
import requests
import json

class TestAPI(unittest.TestCase):
    URL = "https://0.0.0.0:5008/orderdetails"
    
    def test_1_get_order_details(self):
        payload = json.dumps({
          "orderid": "ef39294a-f5d9-4e5f-b002-67a1d1b5851c"
        })

        headers = {
          'Authorization': 'Basic ZXlKMGVYQWlPaUpLVjFRaUxDSmhiR2NpT2lKSVV6STFOaUo5LmV5SnBaQ0k2TXl3aVpYaHdJam94TmpVeE9UazFOVGMxTGpreE5qTjkuTWR2cy04a0cwMVlSUkVQNUhfdUdRUVZaRkRybmIxX01HWUlqNkg0V2xNMDo=',
          'Content-Type': 'application/json'
        }
        
        resp = requests.request("GET", self.URL, headers=headers, data=payload, verify=False)

        self.assertEqual(resp.status_code,200)
        self.assertEqual(len(resp.json()), 7)
        print("Test 1 passed")


if __name__ =="__main__":
    tester = TestAPI()
    tester.test_1_get_order_details()
