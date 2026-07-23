"""
Test Iowa Boundary and Field Boundaries Display
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/local-data"

def test_iowa_boundary():
    """Test Iowa state boundary endpoint"""
    print("\n🗺️  Testing Iowa State Boundary...")
    try:
        response = requests.get(f"{BASE_URL}/boundary")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Boundary loaded: {data['type']}")
            print(f"   📊 Features: {len(data['features'])}")
            if data['features']:
                geom_type = data['features'][0]['geometry']['type']
                print(f"   📐 Geometry: {geom_type}")
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


def test_iowa_fields():
    """Test Iowa field boundaries endpoint"""
    print("\n🌾 Testing Iowa Field Boundaries...")
    try:
        response = requests.get(f"{BASE_URL}/fields")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Fields loaded: {data['type']}")
            print(f"   📊 Features: {len(data['features'])}")
            if data['features']:
                geom_type = data['features'][0]['geometry']['type']
                print(f"   📐 Geometry: {geom_type}")
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


def main():
    print("=" * 60)
    print("IOWA BOUNDARIES TEST")
    print("=" * 60)
    
    results = {
        "boundary": test_iowa_boundary(),
        "fields": test_iowa_fields()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test.upper()}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"))
    print("=" * 60)


if __name__ == "__main__":
    main()
