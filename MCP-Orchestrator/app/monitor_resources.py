import psutil
import gc
from app.job_worker import job_queue

class ResourceMonitor:
    def __init__(self):
        self.max_memory_percent = 80
        self.max_cpu_percent = 90
    
    def check_resources(self):
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        return {
            "memory_percent": memory.percent,
            "cpu_percent": cpu,
            "memory_available": memory.available,
            "can_accept_job": (
                memory.percent < self.max_memory_percent and 
                cpu < self.max_cpu_percent
            )
        }
    
    async def cleanup_if_needed(self):
        resources = self.check_resources()
        
        if resources["memory_percent"] > 70:
            # Force garbage collection
            gc.collect()
            
            # Clear old results (keep last 10)
            if len(job_queue.job_results) > 10:
                old_jobs = list(job_queue.job_results.keys())[:-10]
                for job_id in old_jobs:
                    del job_queue.job_results[job_id]

resource_monitor = ResourceMonitor()