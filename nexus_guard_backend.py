import networkx as nx
import random


class SimulationEngine:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_base_network()

    def _build_base_network(self):
        nodes_data = [
            ("node_01", {"name": "Central Power Substation", "type": "power", "capacity": 100, "current_load": 75, "status": "active", "lat": 12.9716, "lon": 77.5946}),
            ("node_02", {"name": "North Water Treatment", "type": "water", "capacity": 80, "current_load": 60, "status": "active", "lat": 12.9850, "lon": 77.5800}),
            ("node_03", {"name": "City General Hospital", "type": "hospital", "capacity": 50, "current_load": 40, "status": "active", "lat": 12.9600, "lon": 77.5900}),
            ("node_04", {"name": "Main Highway Corridor", "type": "road", "capacity": 120, "current_load": 90, "status": "active", "lat": 12.9750, "lon": 77.6100}),
            ("node_05", {"name": "East Power Substation", "type": "power", "capacity": 90, "current_load": 70, "status": "active", "lat": 12.9900, "lon": 77.6200}),
        ]
        self.graph.add_nodes_from(nodes_data)
        
        edges_data = [
            ("node_01", "node_02", {"dependency_weight": 0.8}),
            ("node_01", "node_03", {"dependency_weight": 0.9}),
            ("node_05", "node_04", {"dependency_weight": 0.5}),
            ("node_02", "node_03", {"dependency_weight": 0.4}),
        ]
        self.graph.add_edges_from(edges_data)

    def run_simulation(self, disaster_type: str, intensity: float, initial_failures: list, enable_ai: bool):
        for node in self.graph.nodes:
            self.graph.nodes[node]['status'] = 'active'
            
        playbook = []
        interventions = []
        affected_citizens = 0
        economic_loss = 0

        for node_id in initial_failures:
            if node_id in self.graph:
                self.graph.nodes[node_id]['status'] = 'failed'
                affected_citizens += random.randint(5000, 20000)
                economic_loss += random.randint(50000, 150000)

        if "node_01" in initial_failures and intensity > 3.0:
            self.graph.nodes["node_02"]['status'] = 'failed'
            affected_citizens += 15000
            economic_loss += 80000

        if enable_ai:
            playbook.append("1. Isolate primary failed nodes to prevent grid feedback loops.")
            playbook.append("2. Reroute emergency power to critical health facilities.")
            for node, data in self.graph.nodes(data=True):
                if data['status'] == 'failed' and data['type'] in ['hospital', 'water']:
                    data['status'] = 'mitigated'
                    interventions.append({
                        "target": node,
                        "action": "Deployed Mobile Generator",
                        "status_update": "mitigated"
                    })
                    affected_citizens -= 5000
                    economic_loss -= 20000

        total_nodes = self.graph.number_of_nodes()
        failed_assets = sum(1 for n, d in self.graph.nodes(data=True) if d['status'] == 'failed')
        mitigated_assets = sum(1 for n, d in self.graph.nodes(data=True) if d['status'] == 'mitigated')

        # A simple 0-100 severity score blending asset failures with human impact,
        # partially offset by successful AI mitigations. Used to drive the
        # frontend's animated "Grid Stability" gauge.
        severity_index = min(
            100,
            round((failed_assets / total_nodes) * 60 + min(affected_citizens, 100000) / 100000 * 40)
        )
        severity_index = max(0, severity_index - mitigated_assets * 8)
        grid_stability = max(0, 100 - severity_index)

        return {
            "metrics": {
                "failed_assets": failed_assets,
                "mitigated_assets": mitigated_assets,
                "affected_citizens": max(0, affected_citizens),
                "economic_loss": max(0, economic_loss),
                "severity_index": severity_index,
                "grid_stability": grid_stability
            },
            "playbook": playbook,
            "interventions": interventions,
            "updated_nodes": [{"id": n, **d} for n, d in self.graph.nodes(data=True)]
        }