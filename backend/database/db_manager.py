from datetime import datetime

# try to import pymongo; if unavailable or connection fails we will use a simple in-memory store
try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None

class DatabaseManager:
    def __init__(self, connection_string='mongodb://localhost:27017/', db_name='green_mining'):
        self.use_memory = False
        if MongoClient is not None:
            try:
                self.client = MongoClient(connection_string, serverSelectionTimeoutMS=2000)
                # trigger server selection
                self.client.server_info()
                self.db = self.client[db_name]
                self.scans = self.db.scans
                self.components = self.db.components
                self.users = self.db.users
                # Seed component database if empty
                if self.components.count_documents({}) == 0:
                    self._seed_components()
            except Exception:
                print("Warning: MongoDB connection failed, using in-memory database")
                self.use_memory = True
        else:
            print("Warning: pymongo not installed, using in-memory database")
            self.use_memory = True

        # in-memory fallback
        if self.use_memory:
            self._init_memory()

    def _init_memory(self):
        self._mem_scans = []
        self._mem_components = []
        self._mem_users = []
        # seed components
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
        if self.use_memory:
            self._mem_components.extend(components)
            print(f"Seeded {len(components)} components (memory)")
        else:
            self.components.insert_many(components)
            print(f"Seeded {len(components)} components")
    
    def insert_scan(self, scan_data):
        """Insert new scan record"""
        if self.use_memory:
            self._mem_scans.append(scan_data)
            return str(len(self._mem_scans) - 1)
        result = self.scans.insert_one(scan_data)
        return str(result.inserted_id)
    
    def get_scan(self, scan_id):
        """Retrieve scan by ID"""
        if self.use_memory:
            for s in self._mem_scans:
                if s.get('scan_id') == scan_id:
                    return s
            return None
        return self.scans.find_one({'scan_id': scan_id})

    def get_component_by_category(self, category):
        """Return first component entry matching the given category/name"""
        if self.use_memory:
            for c in self._mem_components:
                if c.get('category') == category or c.get('name') == category:
                    return c
            return None
        return self.components.find_one({'$or': [{'category': category}, {'name': category}]})

    def list_components(self):
        """Return list of all component definitions"""
        if self.use_memory:
            return list(self._mem_components)
        return list(self.components.find({}))
    
    def get_overall_stats(self):
        """Get aggregate statistics"""
        if self.use_memory:
            total_scans = len(self._mem_scans)
            total_components = sum(s.get('total_components', 0) for s in self._mem_scans)
            total_value = sum(s.get('total_value', 0) for s in self._mem_scans)
            avg_recyclability = (sum(s.get('recyclability_score', 0) for s in self._mem_scans) / total_scans) if total_scans else 0
            # category breakdown for mem
            breakdown = {}
            for s in self._mem_scans:
                for det in s.get('detections', []):
                    cat = det.get('component_category', det.get('component'))
                    breakdown[cat] = breakdown.get(cat, 0) + 1
            return {
                'total_scans': total_scans,
                'total_components_detected': total_components,
                'total_value_estimated': round(total_value, 2),
                'avg_recyclability_score': round(avg_recyclability, 1),
                'category_breakdown': breakdown
            }

        # compute totals with aggregation
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
                'avg_recyclability_score': round(stats.get('avg_recyclability', 0), 1),
                'category_breakdown': breakdown
            }
        else:
            return {
                'total_scans': 0,
                'total_components_detected': 0,
                'total_value_estimated': 0,
                'avg_recyclability_score': 0,
                'category_breakdown': breakdown
            }
