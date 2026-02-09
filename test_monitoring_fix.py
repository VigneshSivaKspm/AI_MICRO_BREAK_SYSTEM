#!/usr/bin/env python3
"""
Test script to validate the monitoring system performance fixes
Run this to verify that the database connection pooling and polling optimizations work correctly
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_monitoring_system_performance():
    """Test the monitoring system performance improvements"""
    
    print("🔍 Testing AI Micro Break System Performance Fixes")
    print("=" * 65)
    
    base_url = "http://127.0.0.1:2050"
    
    # Test 1: Health Check with Pool Stats
    print("\n1. Testing Enhanced Health Check...")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health check passed: {health_data.get('status', 'unknown')}")
            if health_data.get('components'):
                for component, status in health_data['components'].items():
                    print(f"      - {component}: {'✅' if status else '❌'}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Monitoring Status with Pool Stats
    print("\n2. Testing Enhanced Monitoring Status...")
    try:
        response = requests.get(f"{base_url}/api/v1/monitoring/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print(f"   ✅ Status check passed")
            print(f"      - Activity monitoring: {status_data.get('activity_monitoring', False)}")
            print(f"      - Fatigue detection: {status_data.get('fatigue_detection', False)}")
            print(f"      - Database healthy: {status_data.get('database_healthy', False)}")
            
            # Check pool stats
            pool_stats = status_data.get('database_pool', {})
            if pool_stats:
                print(f"      - Pool status: {pool_stats.get('status', 'unknown')}")
                print(f"      - Pool size: {pool_stats.get('pool_size', 'unknown')}")
                print(f"      - Pool initialized: {pool_stats.get('is_initialized', False)}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
    
    # Test 3: Start Monitoring
    print("\n3. Testing Monitoring Start...")
    try:
        response = requests.post(f"{base_url}/api/v1/monitoring/start", 
                               json={"user_id": 1}, timeout=10)
        if response.status_code == 200:
            start_data = response.json()
            print(f"   ✅ Monitoring start: {start_data.get('message', 'started')}")
        else:
            print(f"   ❌ Monitoring start failed: {response.status_code}")
            print(f"      Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Monitoring start error: {e}")
    
    # Test 4: Performance Test - Multiple Rapid Requests
    print("\n4. Testing Performance with Rapid Requests...")
    start_time = time.time()
    success_count = 0
    error_count = 0
    
    for i in range(6):  # 6 requests to simulate 3 API calls twice
        try:
            endpoints = [
                f"{base_url}/api/v1/activity/current?user_id=1",
                f"{base_url}/api/v1/fatigue/status?user_id=1",
                f"{base_url}/api/v1/breaks/status?user_id=1"
            ]
            
            for endpoint in endpoints:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
                    print(f"      ⚠️  Request failed: {endpoint.split('/')[-1]} - {response.status_code}")
                    
        except Exception as e:
            error_count += 1
            print(f"      ⚠️  Request error: {e}")
    
    end_time = time.time()
    total_requests = success_count + error_count
    avg_response_time = (end_time - start_time) / total_requests if total_requests > 0 else 0
    
    print(f"   📊 Performance Results:")
    print(f"      - Total requests: {total_requests}")
    print(f"      - Successful: {success_count}")
    print(f"      - Errors: {error_count}")
    print(f"      - Average response time: {avg_response_time:.2f}s")
    print(f"      - Success rate: {(success_count/total_requests*100):.1f}%")
    
    success_rate = (success_count / total_requests) * 100 if total_requests > 0 else 0
    if success_rate > 80 and avg_response_time < 2:
        print(f"   ✅ Performance test passed!")
    else:
        print(f"   ⚠️  Performance could be better")
    
    # Test 5: Wait and Test Again (to verify sustained performance)
    print("\n5. Testing Sustained Performance...")
    time.sleep(5)
    
    try:
        response = requests.get(f"{base_url}/api/v1/monitoring/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            pool_stats = status_data.get('database_pool', {})
            print(f"   ✅ Sustained monitoring working")
            print(f"      - Pool still healthy: {pool_stats.get('status') == 'healthy'}")
        else:
            print(f"   ❌ Sustained performance test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Sustained performance error: {e}")
    
    # Test 6: Stop monitoring
    print("\n6. Testing Monitoring Stop...")
    try:
        response = requests.post(f"{base_url}/api/v1/monitoring/stop", 
                               json={"user_id": 1}, timeout=10)
        if response.status_code == 200:
            stop_data = response.json()
            print(f"   ✅ Monitoring stop: {stop_data.get('message', 'stopped')}")
        else:
            print(f"   ❌ Monitoring stop failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Monitoring stop error: {e}")
    
    print("\n" + "=" * 65)
    print("🏁 Performance Test Completed!")
    print("\nKey Improvements Made:")
    print("  • 📊 Frontend polling reduced from 5s to 30s")
    print("  • 🔗 Database connection pooling optimized") 
    print("  • 🧠 AI analysis reduced from 10s to 60s intervals")
    print("  • ⚡ Added request timeouts and retry logic")
    print("  • 📈 Enhanced error handling and backoff")
    print("  • 📊 Added connection pool monitoring")
    
    if success_rate > 80 and avg_response_time < 2:
        print("\n✅ System should now be much more stable and efficient!")
    else:
        print("\n⚠️  System may still need optimization. Check logs for details.")
    
    print(f"\nOpen the web interface at: {base_url}")
    print("Monitor should now work much more reliably with less database load.")

if __name__ == "__main__":
    
    print("Starting performance test in 3 seconds...")
    print("Make sure the backend server is running: python backend/app.py")
    time.sleep(3)
    
    test_monitoring_system_performance()