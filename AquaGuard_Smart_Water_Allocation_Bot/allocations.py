from config import (
    PER_CAPITA_DOMESTIC, AGRICULTURAL_BENCHMARK, INDUSTRIAL_BENCHMARK,
    RESERVOIR_SAFE_LEVEL, RESERVOIR_LEVELS, TOTAL_SUPPLIES
)

class AllocationProcessor:
    def __init__(self, water_alloc):
        self.water_alloc = water_alloc
        
    def parse_request(self, request_text):
        try:
            parts = [p.strip() for p in request_text.split(',')]
            region = int(parts[0].split(':')[1].strip())
            population = int(parts[1].split(':')[1].strip())
            sector = parts[2].split(':')[1].strip().lower()
            volume = float(parts[3].split(':')[1].strip())
            cycle = int(parts[4].split(':')[1].strip())
            return region, population, sector, volume, cycle, None
        except Exception as e:
            return None, None, None, None, None, f"Invalid request format: {str(e)}"

    def process_request(self, request_text, drought_mode):
        region, population, sector, volume, cycle, error = self.parse_request(request_text)
        if error:
            return error, "error"
            
        if sector not in ['domestic', 'agricultural', 'industrial']:
            return "Invalid sector", "error"
            
        if sector in self.water_alloc.allocations[region][cycle]:
            return f"Duplicate request", "error"

        level = RESERVOIR_LEVELS.get(region, 100)
        total_supply = TOTAL_SUPPLIES.get(region, 0)
        allocated = sum(self.water_alloc.allocations[region][cycle].values())
        available = total_supply * level / 100 - allocated

        benchmark = self.get_benchmark(sector, population, drought_mode)
        
        if volume > benchmark:
            volume = benchmark
            
        if level < RESERVOIR_SAFE_LEVEL and sector != 'domestic':
            return f"Rejected due to reservoir safety", "rejected"
            
        if drought_mode and sector != 'domestic':
            return f"Rejected due to drought mode", "rejected"

        if volume > available:
            volume = max(0, available)

        if volume <= 0:
            return f"Rejected due to insufficient supply", "rejected"

        decision = "Approved" if volume == benchmark else "Reduced"
        reason = f"Allocated {volume:.0f} liters"
        
        self.water_alloc.add_allocation(region, cycle, sector, volume, decision, reason)
        return f"{decision}: {reason}", decision.lower()

    def get_benchmark(self, sector, population, drought_mode):
        if sector == 'domestic':
            benchmark = population * PER_CAPITA_DOMESTIC
        elif sector == 'agricultural':
            benchmark = AGRICULTURAL_BENCHMARK
        else:
            benchmark = INDUSTRIAL_BENCHMARK
            
        if drought_mode:
            benchmark /= 2
        return benchmark