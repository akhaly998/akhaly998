#!/usr/bin/env python3
"""
Test script for the Name Similarity Checker API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🔍 Testing Name Similarity Checker API\n")
    
    # Test the main functionality with the provided name
    test_name = "صدام حسن سعيد مجيد"
    print(f"Testing with name: {test_name}")
    
    # Test check-name endpoint
    print("\n1. Testing /check-name endpoint:")
    response = requests.post(f"{BASE_URL}/check-name", 
                           json={"name": test_name, "threshold": 60.0})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Input name: {result['input_name']}")
        print(f"✅ Is match: {result['is_match']}")
        print(f"✅ Highest similarity: {result['highest_similarity']}%")
        
        if result['matches']:
            print("✅ Matches found:")
            for match in result['matches']:
                print(f"   - {match['blacklist_name']} ({match['similarity_score']}%) - {match['category']}")
        else:
            print("❌ No matches found")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test similarity endpoint
    print(f"\n2. Testing /similarity/{test_name} endpoint:")
    response = requests.get(f"{BASE_URL}/similarity/{test_name}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Top 5 similarity scores:")
        for i, entry in enumerate(result['results'][:5]):
            max_score = entry['similarity_scores']['max_score']
            print(f"   {i+1}. {entry['blacklist_name']} - {max_score}% ({entry['category']})")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test blacklist endpoint
    print(f"\n3. Testing /blacklist endpoint:")
    response = requests.get(f"{BASE_URL}/blacklist")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Total blacklist entries: {result['total_entries']}")
        print("✅ Sample entries:")
        for entry in result['blacklist'][:3]:
            print(f"   - {entry['name']} ({entry['category']})")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test with different threshold
    print(f"\n4. Testing with high threshold (90%):")
    response = requests.post(f"{BASE_URL}/check-name", 
                           json={"name": test_name, "threshold": 90.0})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Matches with 90% threshold: {len(result['matches'])}")
        if result['matches']:
            for match in result['matches']:
                print(f"   - {match['blacklist_name']} ({match['similarity_score']}%)")
    
    print("\n🎉 API testing completed!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")