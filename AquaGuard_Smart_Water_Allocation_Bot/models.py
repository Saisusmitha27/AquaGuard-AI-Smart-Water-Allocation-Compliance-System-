import time
import hashlib
import json
from collections import defaultdict

class AuditTrail:
    def __init__(self):
        self.chain = []
        
    def add_block(self, data):
        block = {
            'index': len(self.chain),
            'timestamp': time.time(),
            'data': data,
            'previous_hash': self.hash_block(self.chain[-1]) if self.chain else '0'
        }
        block['hash'] = self.hash_block(block)
        self.chain.append(block)
        return block
    
    def hash_block(self, block):
        block_string = f"{block['index']}{block['timestamp']}{block['data']}{block['previous_hash']}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def verify_chain(self):
        for i in range(1, len(self.chain)):
            if self.chain[i]['previous_hash'] != self.hash_block(self.chain[i-1]):
                return False
        return True
    
    def get_audit_report(self):
        return [
            {
                'index': b['index'],
                'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(b['timestamp'])),
                'data': b['data'],
                'hash': b['hash'][:8] + '...'
            }
            for b in self.chain
        ]

class WaterAllocation:
    def __init__(self):
        self.allocations = defaultdict(lambda: defaultdict(dict))
        self.logs = []
        self.audit = AuditTrail()
        
    def add_allocation(self, region, cycle, sector, volume, decision, reason):
        self.allocations[region][cycle][sector] = volume
        log_entry = {
            "timestamp": time.time(),
            "region": region,
            "sector": sector,
            "allocated": volume,
            "decision": decision,
            "reason": reason,
            "cycle": cycle
        }
        self.logs.append(log_entry)
        self.audit.add_block(json.dumps(log_entry))
        return log_entry