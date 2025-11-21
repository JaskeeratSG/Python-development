"""
Performance Comparison: Sync vs Async
=====================================

This script demonstrates the performance difference between
synchronous and asynchronous implementations.
"""

import asyncio
import time
import aiohttp
import requests
from typing import List
import statistics

class PerformanceTester:
    """Test performance of sync vs async implementations"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.sync_url = f"{base_url}"  # Your sync API
        self.async_url = f"{base_url}"  # Your async API
    
    async def test_async_performance(self, num_requests: int = 100) -> dict:
        """Test async performance"""
        print(f"🔄 Testing async performance with {num_requests} requests...")
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(num_requests):
                task = self._make_async_request(session, i)
                tasks.append(task)
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        successful_requests = [r for r in results if not isinstance(r, Exception)]
        failed_requests = [r for r in results if isinstance(r, Exception)]
        
        return {
            "total_requests": num_requests,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
            "average_response_time": total_time / num_requests,
            "success_rate": len(successful_requests) / num_requests * 100
        }
    
    def test_sync_performance(self, num_requests: int = 100) -> dict:
        """Test sync performance"""
        print(f"🔄 Testing sync performance with {num_requests} requests...")
        
        start_time = time.time()
        
        results = []
        for i in range(num_requests):
            try:
                response = self._make_sync_request(i)
                results.append(response)
            except Exception as e:
                results.append(e)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        successful_requests = [r for r in results if not isinstance(r, Exception)]
        failed_requests = [r for r in results if isinstance(r, Exception)]
        
        return {
            "total_requests": num_requests,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
            "average_response_time": total_time / num_requests,
            "success_rate": len(successful_requests) / num_requests * 100
        }
    
    async def _make_async_request(self, session: aiohttp.ClientSession, request_id: int):
        """Make an async HTTP request"""
        try:
            async with session.get(f"{self.async_url}/health") as response:
                return await response.json()
        except Exception as e:
            return e
    
    def _make_sync_request(self, request_id: int):
        """Make a sync HTTP request"""
        try:
            response = requests.get(f"{self.sync_url}/health", timeout=10)
            return response.json()
        except Exception as e:
            return e
    
    def print_comparison(self, sync_results: dict, async_results: dict):
        """Print performance comparison"""
        print("\n" + "="*60)
        print("📊 PERFORMANCE COMPARISON: SYNC vs ASYNC")
        print("="*60)
        
        print(f"\n🔄 Sync Results:")
        print(f"  Total Requests: {sync_results['total_requests']}")
        print(f"  Successful: {sync_results['successful_requests']}")
        print(f"  Failed: {sync_results['failed_requests']}")
        print(f"  Total Time: {sync_results['total_time']:.2f}s")
        print(f"  Requests/sec: {sync_results['requests_per_second']:.2f}")
        print(f"  Avg Response Time: {sync_results['average_response_time']:.3f}s")
        print(f"  Success Rate: {sync_results['success_rate']:.1f}%")
        
        print(f"\n⚡ Async Results:")
        print(f"  Total Requests: {async_results['total_requests']}")
        print(f"  Successful: {async_results['successful_requests']}")
        print(f"  Failed: {async_results['failed_requests']}")
        print(f"  Total Time: {async_results['total_time']:.2f}s")
        print(f"  Requests/sec: {async_results['requests_per_second']:.2f}")
        print(f"  Avg Response Time: {async_results['average_response_time']:.3f}s")
        print(f"  Success Rate: {async_results['success_rate']:.1f}%")
        
        # Calculate improvements
        speed_improvement = async_results['requests_per_second'] / sync_results['requests_per_second']
        time_improvement = sync_results['total_time'] / async_results['total_time']
        
        print(f"\n🚀 Performance Improvements:")
        print(f"  Speed Improvement: {speed_improvement:.2f}x faster")
        print(f"  Time Improvement: {time_improvement:.2f}x faster")
        
        if speed_improvement > 1.5:
            print("  ✅ Async shows significant performance improvement!")
        elif speed_improvement > 1.1:
            print("  ✅ Async shows moderate performance improvement")
        else:
            print("  ⚠️  Async improvement is minimal (may be due to simple endpoints)")

async def demonstrate_async_benefits():
    """Demonstrate the benefits of async programming"""
    print("🎯 Async Programming Benefits Demonstration")
    print("=" * 50)
    
    print("\n📚 Key Benefits of Async:")
    print("1. 🔄 Concurrency: Handle multiple requests simultaneously")
    print("2. ⚡ Performance: Better resource utilization")
    print("3. 📈 Scalability: Handle more users with same resources")
    print("4. 🎯 I/O Bound Operations: Perfect for database calls, API requests")
    print("5. 💾 Memory Efficiency: Lower memory usage per request")
    
    print("\n🔄 When to Use Async:")
    print("✅ High concurrency applications")
    print("✅ I/O bound operations (database, APIs)")
    print("✅ Real-time applications")
    print("✅ Microservices")
    print("✅ Web scraping")
    print("✅ Chat applications")
    
    print("\n⚠️  When NOT to Use Async:")
    print("❌ CPU-bound tasks (use multiprocessing instead)")
    print("❌ Simple, low-traffic applications")
    print("❌ When sync code is already working well")
    print("❌ Team unfamiliar with async concepts")
    
    print("\n🛠️  Implementation Considerations:")
    print("• Use async/await consistently throughout the stack")
    print("• Choose async-compatible libraries (aiohttp, asyncpg, etc.)")
    print("• Handle async database sessions properly")
    print("• Use async context managers for resource cleanup")
    print("• Test thoroughly - async can be tricky to debug")

async def main():
    """Main function to run performance tests"""
    print("🚀 CRUD API Performance Comparison")
    print("=" * 40)
    
    # Demonstrate async benefits
    await demonstrate_async_benefits()
    
    # Note: Actual performance testing requires running servers
    print("\n📝 To run actual performance tests:")
    print("1. Start your sync API: python main.py")
    print("2. Start your async API: python async_main.py")
    print("3. Run: python performance_comparison.py")
    
    print("\n💡 Key Takeaways:")
    print("• Async is beneficial for I/O bound operations")
    print("• Database operations are perfect for async")
    print("• Use async when you expect high concurrency")
    print("• Async requires async-compatible libraries")
    print("• Consider your team's async experience")

if __name__ == "__main__":
    asyncio.run(main())
