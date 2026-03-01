import requests
import json
import time

API_URL = "http://localhost:5000/api"

def test_health():
    response = requests.get(f"{API_URL}/health")
    print(f"Health Check: {response.json()}")


def test_upload(image_path):
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(f"{API_URL}/scan", files=files)
        print(f"Upload Response: {response.json()}")
        return response.json().get('scan_id')


def test_get_results(scan_id):
    response = requests.get(f"{API_URL}/scan/{scan_id}")
    print(f"Results: {json.dumps(response.json(), indent=2)}")


def test_stats():
    response = requests.get(f"{API_URL}/stats")
    print(f"Stats: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("Testing Green Mining AI API")
    test_health()
    # replace with a real sample image path
    # scan_id = test_upload("sample_pcb.jpg")
    # if scan_id:
    #     time.sleep(2)  # wait for processing
    #     test_get_results(scan_id)
    #     test_stats()
