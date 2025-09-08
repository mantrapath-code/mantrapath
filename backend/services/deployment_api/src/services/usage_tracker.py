"""
Usage Tracker Service for monitoring frontend engineer API usage
"""

import time
from typing import Dict, Any, List
from datetime import datetime, timezone
from collections import defaultdict


class UsageTrackerService:
    """Service for tracking frontend engineer API usage"""
    
    def __init__(self):
        # Store usage data: {engineer_id: {endpoint: [timestamps]}}
        self.usage_data = defaultdict(lambda: defaultdict(list))
        
        # Store metrics: {engineer_id: {metric: value}}
        self.metrics = defaultdict(lambda: defaultdict(int))
        
        # Cleanup old data every hour
        self.cleanup_interval = 3600
        self.last_cleanup = time.time()
    
    async def initialize(self):
        """Initialize the service"""
        pass
    
    async def cleanup(self):
        """Cleanup resources"""
        pass
    
    async def track_api_call(self, engineer_id: str, endpoint: str, status: str):
        """Track an API call made by a frontend engineer"""
        try:
            current_time = time.time()
            
            # Add timestamp to usage data
            self.usage_data[engineer_id][endpoint].append(current_time)
            
            # Update metrics
            self.metrics[engineer_id]["total_calls"] += 1
            if status == "success":
                self.metrics[engineer_id]["successful_calls"] += 1
            else:
                self.metrics[engineer_id]["failed_calls"] += 1
            
            # Cleanup old data periodically
            if current_time - self.last_cleanup > self.cleanup_interval:
                await self._cleanup_old_data()
                self.last_cleanup = current_time
                
        except Exception as e:
            print(f"Failed to track API call: {e}")
    
    async def get_engineer_metrics(self, engineer_id: str) -> Dict[str, Any]:
        """Get usage metrics for a specific engineer"""
        try:
            current_time = time.time()
            
            # Calculate hourly, daily, and monthly usage
            hourly_usage = await self._get_period_usage(engineer_id, current_time - 3600)
            daily_usage = await self._get_period_usage(engineer_id, current_time - 86400)
            monthly_usage = await self._get_period_usage(engineer_id, current_time - 2592000)
            
            # Get endpoint-specific usage
            endpoint_usage = {}
            for endpoint, timestamps in self.usage_data[engineer_id].items():
                # Remove old timestamps
                recent_timestamps = [ts for ts in timestamps if ts > current_time - 86400]
                endpoint_usage[endpoint] = {
                    "last_24h": len(recent_timestamps),
                    "total": len(timestamps)
                }
            
            # Calculate success rate
            total_calls = self.metrics[engineer_id]["total_calls"]
            successful_calls = self.metrics[engineer_id]["successful_calls"]
            success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
            
            return {
                "engineer_id": engineer_id,
                "usage_summary": {
                    "last_hour": hourly_usage,
                    "last_24_hours": daily_usage,
                    "last_30_days": monthly_usage,
                    "total_calls": total_calls
                },
                "performance": {
                    "success_rate": f"{success_rate:.1f}%",
                    "successful_calls": successful_calls,
                    "failed_calls": self.metrics[engineer_id]["failed_calls"]
                },
                "endpoint_usage": endpoint_usage,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get metrics for {engineer_id}: {str(e)}"}
    
    async def get_all_engineers_metrics(self) -> Dict[str, Any]:
        """Get usage metrics for all engineers"""
        try:
            all_metrics = {}
            
            for engineer_id in self.usage_data.keys():
                all_metrics[engineer_id] = await self.get_engineer_metrics(engineer_id)
            
            # Calculate system-wide metrics
            total_engineers = len(all_metrics)
            total_calls = sum(m.get("usage_summary", {}).get("total_calls", 0) for m in all_metrics.values())
            avg_success_rate = 0
            
            if total_engineers > 0:
                success_rates = []
                for metrics in all_metrics.values():
                    if "performance" in metrics and "success_rate" in metrics["performance"]:
                        try:
                            rate = float(metrics["performance"]["success_rate"].replace("%", ""))
                            success_rates.append(rate)
                        except:
                            pass
                
                if success_rates:
                    avg_success_rate = sum(success_rates) / len(success_rates)
            
            return {
                "summary": {
                    "total_engineers": total_engineers,
                    "total_api_calls": total_calls,
                    "average_success_rate": f"{avg_success_rate:.1f}%"
                },
                "engineers": all_metrics,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get all engineers metrics: {str(e)}"}
    
    async def get_endpoint_usage(self, endpoint: str) -> Dict[str, Any]:
        """Get usage statistics for a specific endpoint"""
        try:
            current_time = time.time()
            endpoint_usage = {}
            
            for engineer_id, endpoints in self.usage_data.items():
                if endpoint in endpoints:
                    timestamps = endpoints[endpoint]
                    
                    # Calculate recent usage
                    hourly = len([ts for ts in timestamps if ts > current_time - 3600])
                    daily = len([ts for ts in timestamps if ts > current_time - 86400])
                    weekly = len([ts for ts in timestamps if ts > current_time - 604800])
                    
                    endpoint_usage[engineer_id] = {
                        "last_hour": hourly,
                        "last_24_hours": daily,
                        "last_week": weekly,
                        "total": len(timestamps)
                    }
            
            # Calculate total usage
            total_hourly = sum(u["last_hour"] for u in endpoint_usage.values())
            total_daily = sum(u["last_24_hours"] for u in endpoint_usage.values())
            total_weekly = sum(u["last_week"] for u in endpoint_usage.values())
            total_overall = sum(u["total"] for u in endpoint_usage.values())
            
            return {
                "endpoint": endpoint,
                "usage_summary": {
                    "total_engineers": len(endpoint_usage),
                    "last_hour": total_hourly,
                    "last_24_hours": total_daily,
                    "last_week": total_weekly,
                    "total_calls": total_overall
                },
                "engineer_usage": endpoint_usage,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get endpoint usage: {str(e)}"}
    
    async def get_usage_trends(self, engineer_id: str, period: str = "daily") -> Dict[str, Any]:
        """Get usage trends for an engineer over time"""
        try:
            current_time = time.time()
            
            if period == "hourly":
                intervals = 24
                interval_size = 3600
            elif period == "daily":
                intervals = 30
                interval_size = 86400
            elif period == "weekly":
                intervals = 12
                interval_size = 604800
            else:
                return {"error": "Invalid period. Use 'hourly', 'daily', or 'weekly'"}
            
            trends = []
            
            for i in range(intervals):
                start_time = current_time - (i * interval_size)
                end_time = start_time + interval_size
                
                # Count calls in this interval
                interval_calls = 0
                for endpoint, timestamps in self.usage_data[engineer_id].items():
                    interval_calls += len([ts for ts in timestamps if start_time <= ts < end_time])
                
                trends.append({
                    "period": i,
                    "start_time": datetime.fromtimestamp(start_time, timezone.utc).isoformat(),
                    "end_time": datetime.fromtimestamp(end_time, timezone.utc).isoformat(),
                    "calls": interval_calls
                })
            
            # Reverse to show oldest first
            trends.reverse()
            
            return {
                "engineer_id": engineer_id,
                "period": period,
                "trends": trends,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get usage trends: {str(e)}"}
    
    async def _get_period_usage(self, engineer_id: str, since_time: float) -> int:
        """Get usage count for an engineer since a specific time"""
        try:
            total_calls = 0
            
            for endpoint, timestamps in self.usage_data[engineer_id].items():
                recent_calls = len([ts for ts in timestamps if ts > since_time])
                total_calls += recent_calls
            
            return total_calls
            
        except Exception as e:
            print(f"Failed to get period usage: {e}")
            return 0
    
    async def _cleanup_old_data(self):
        """Clean up old usage data to prevent memory bloat"""
        try:
            current_time = time.time()
            cutoff_time = current_time - 2592000  # 30 days
            
            for engineer_id in list(self.usage_data.keys()):
                for endpoint in list(self.usage_data[engineer_id].keys()):
                    # Remove old timestamps
                    self.usage_data[engineer_id][endpoint] = [
                        ts for ts in self.usage_data[engineer_id][endpoint] 
                        if ts > cutoff_time
                    ]
                    
                    # Remove empty endpoint entries
                    if not self.usage_data[engineer_id][endpoint]:
                        del self.usage_data[engineer_id][endpoint]
                
                # Remove empty engineer entries
                if not self.usage_data[engineer_id]:
                    del self.usage_data[engineer_id]
                    
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    async def reset_engineer_usage(self, engineer_id: str) -> bool:
        """Reset usage data for an engineer (for admin purposes)"""
        try:
            if engineer_id in self.usage_data:
                del self.usage_data[engineer_id]
            if engineer_id in self.metrics:
                del self.metrics[engineer_id]
            return True
        except Exception as e:
            print(f"Reset error: {e}")
            return False
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide usage statistics"""
        try:
            total_engineers = len(self.usage_data)
            total_endpoints = sum(len(endpoints) for endpoints in self.usage_data.values())
            
            # Calculate total calls across all engineers
            total_calls = sum(self.metrics[engineer_id]["total_calls"] for engineer_id in self.metrics)
            
            # Calculate average calls per engineer
            avg_calls_per_engineer = total_calls / total_engineers if total_engineers > 0 else 0
            
            return {
                "summary": {
                    "total_engineers": total_engineers,
                    "total_endpoints": total_endpoints,
                    "total_api_calls": total_calls,
                    "average_calls_per_engineer": round(avg_calls_per_engineer, 2)
                },
                "last_cleanup": self.last_cleanup,
                "cleanup_interval": self.cleanup_interval,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get system stats: {str(e)}"}

