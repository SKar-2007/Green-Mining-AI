from pymongo import MongoClient
from datetime import datetime

class DatabaseManager:
    def __init__(self, connection_string='mongodb://localhost:27017/', db_name='green_mining'):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.scans = self.db.scans
        self.components = self.db.components
        self.users = self.db.users
        
        # Seed component database if empty
        if self.components.count_documents({}) == 0:
            self._seed_components()
    
    def _seed_components(self):
        """Seed initial component database"""
        components = [
            {
                'name': 'Generic IC',
                'category': 'IC',
                'materials': {'gold_mg': 0.2, 'copper_g': 5, 'silicon_g': 2},
                'market_value_usd': 5.50,
                'recyclability_score': 90
            },
            {
                'name': 'Electrolytic Capacitor',
                'category': 'Capacitor',
                'materials': {'aluminum_g': 2, 'copper_g': 0.5},
                'market_value_usd': 0.15,
                'recyclability_score': 70
            },
            # Additional components can be added here for MVP
        ]
        self.components.insert_many(components)
        print(f"Seeded {len(components)} components")
    
    def insert_scan(self, scan_data):
        """Insert new scan record"""
        result = self.scans.insert_one(scan_data)
        return str(result.inserted_id)
    
    def get_scan(self, scan_id):
        """Retrieve scan by ID"""
        return self.scans.find_one({'scan_id': scan_id})
    
    def get_overall_stats(self):
        """Get aggregate statistics"""
        total_scans = self.scans.count_documents({})
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_components': {'$sum': '$total_components'},
                    'total_value': {'$sum': '$total_value'},
                    'avg_recyclability': {'$avg': '$recyclability_score'}
                }
            }
        ]
        result = list(self.scans.aggregate(pipeline))
        if result:
            stats = result[0]
            return {
                'total_scans': total_scans,
                'total_components_detected': stats.get('total_components', 0),
                'total_value_estimated': round(stats.get('total_value', 0), 2),
                'avg_recyclability_score': round(stats.get('avg_recyclability', 0), 1)
            }
        else:
            return {
                'total_scans': 0,
                'total_components_detected': 0,
                'total_value_estimated': 0,
                'avg_recyclability_score': 0
            }
