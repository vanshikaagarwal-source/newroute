import networkx as nx
import sys
import json
import heapq

G = nx.Graph()

# Locations
G.add_nodes_from([
    "Guwahati",
    "Shillong",
    "Silchar",
    "Aizawl",
    "Agartala",
    "Imphal"
])

# Roads
G.add_edge("Guwahati", "Shillong", distance=100, time=180, risk=2)
G.add_edge("Guwahati", "Silchar", distance=300, time=360, risk=3)
G.add_edge("Shillong", "Silchar", distance=320, time=420, risk=4)
G.add_edge("Silchar", "Aizawl", distance=180, time=200, risk=1)
G.add_edge("Silchar", "Agartala", distance=400, time=500, risk=5)
G.add_edge("Aizawl", "Imphal", distance=400, time=600, risk=4)
G.add_edge("Agartala", "Imphal", distance=350, time=540, risk=3)

# Calculate combined road cost
for u, v, data in G.edges(data=True):
    data["cost"] = data["distance"] + data["time"] + (data["risk"] * 10)


def find_route(graph, start, destination):
    return nx.shortest_path(
        graph,
        start,
        destination,
        weight="cost"
    )


def route_details(graph, route):
    distance = nx.path_weight(graph, route, weight="distance")
    time = nx.path_weight(graph, route, weight="time")

    risk = sum(
        graph[route[i]][route[i + 1]]["risk"]
        for i in range(len(route) - 1)
    )

    return distance, time, risk


def road_is_blocked(route, blocked_road):
    for i in range(len(route) - 1):
        road = (route[i], route[i + 1])

        if road == blocked_road or road == blocked_road[::-1]:
            return True

    return False


# Trucks
trucks = [
    {
        "id": "Truck-1",
        "start": "Guwahati",
        "destination": "Imphal"
    },
    {
        "id": "Truck-2",
        "start": "Shillong",
        "destination": "Imphal"
    },
    {
        "id": "Truck-3",
        "start": "Guwahati",
        "destination": "Agartala"
    }
]


def simulate_blockage(blocked_start, blocked_end):

    blocked_road = (blocked_start, blocked_end)

    # Temporary graph without blocked road
    temp_graph = G.copy()

    if not temp_graph.has_edge(blocked_start, blocked_end):
        return {
            "success": False,
            "error": "Blocked road does not exist"
        }

    temp_graph.remove_edge(blocked_start, blocked_end)

    results = []
    priority_queue = []

    for truck in trucks:

        original_route = find_route(
            G,
            truck["start"],
            truck["destination"]
        )

        original_distance, original_time, original_risk = route_details(
            G,
            original_route
        )

        affected = road_is_blocked(
            original_route,
            blocked_road
        )

        if affected:

            try:
                new_route = find_route(
                    temp_graph,
                    truck["start"],
                    truck["destination"]
                )

                new_distance, new_time, new_risk = route_details(
                    temp_graph,
                    new_route
                )

                # Priority score:
                # higher delay + higher risk = higher priority
                delay = new_time - original_time
                priority = delay + (new_risk * 10)

                heapq.heappush(
                    priority_queue,
                    (-priority, truck["id"])
                )

                results.append({
                    "id": truck["id"],
                    "affected": True,
                    "originalRoute": original_route,
                    "reroutedRoute": new_route,
                    "distance": new_distance,
                    "time": new_time,
                    "risk": new_risk,
                    "delay": delay,
                    "priority": priority
                })

            except nx.NetworkXNoPath:

                heapq.heappush(
                    priority_queue,
                    (-9999, truck["id"])
                )
                
                results.append({
                    "id": truck["id"],
                    "affected": True,
                    "originalRoute": original_route,
                    "reroutedRoute": None,
                    "priority": 9999
                })

        else:

            results.append({
                "id": truck["id"],
                "affected": False,
                "originalRoute": original_route,
                "reroutedRoute": original_route,
                "distance": original_distance,
                "time": original_time,
                "risk": original_risk,
                "delay": 0,
                "priority": 0
            })

    # Create priority order
    priority_order = []

    while priority_queue:
        priority, truck_id = heapq.heappop(priority_queue)

        priority_order.append({
            "truck": truck_id,
            "priority": -priority
        })

    return {
        "success": True,
        "blockedRoad": [
            blocked_start,
            blocked_end
        ],
        "trucks": results,
        "priorityQueue": priority_order
    }


def get_route(start, destination, blocked_start=None, blocked_end=None):

    try:

        if blocked_start and blocked_end:

            return simulate_blockage(
                blocked_start,
                blocked_end
            )

        route = find_route(
            G,
            start,
            destination
        )

        distance, time, risk = route_details(
            G,
            route
        )

        return {
            "success": True,
            "route": route,
            "distance": distance,
            "time": time,
            "risk": risk
        }

    except nx.NetworkXNoPath:

        return {
            "success": False,
            "error": "No route available"
        }

    except nx.NodeNotFound:

        return {
            "success": False,
            "error": "Location not found"
        }


if __name__ == "__main__":

    start = sys.argv[1]
    destination = sys.argv[2]

    blocked_start = None
    blocked_end = None

    if len(sys.argv) >= 5:
        blocked_start = sys.argv[3]
        blocked_end = sys.argv[4]

    result = get_route(
        start,
        destination,
        blocked_start,
        blocked_end
    )

    print(json.dumps(result))