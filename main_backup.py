import networkx as nx

G = nx.Graph()

# Locations
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
print("Locations:", G.nodes)
print("Roads:", G.edges)

# Calculate a combined cost for each road
for u, v, data in G.edges(data=True):
    data["cost"] = data["distance"] + data["time"] + (data["risk"] *10 )

# Find the best route using combined cost
def find_route(graph, start, destination):
    route = nx.shortest_path(
        graph,
        start,
        destination,
        weight="cost"
    )
    return route

def route_details(graph, route):
    distance = nx.path_weight(graph, route, weight="distance")
    time = nx.path_weight(graph, route, weight="time")
    risk = sum(
        graph[route[i]][route[i + 1]]["risk"]
        for i in range(len(route) - 1)
    )

    return distance, time, risk

# Find the best route
best_route = find_route(G, "Guwahati", "Imphal")

print("Best route:", best_route)

# Simulate a road blockage
def reroute_after_blockage(graph, blocked_road, start, destination):
    temp_graph = graph.copy()
    temp_graph.remove_edge(blocked_road[0], blocked_road[1])
    try:
        new_route = nx.shortest_path(
            temp_graph,
            start,
            destination,
            weight="cost"
        )

        total_distance = nx.path_weight(
            temp_graph,
            new_route,
            weight="distance"
        )

        return new_route, total_distance

    except nx.NetworkXNoPath:
        return None, 0
    
new_route, total_distance = reroute_after_blockage(
    G,
    ("Silchar", "Aizawl"),
    "Guwahati",
    "Imphal"
)
if new_route:
    print("Route after blockage:", new_route)
    print("Total distance:", total_distance, "km")
else:
    print("No alternate route available")

trucks = [
    {"id": "Truck-1", "start": "Guwahati", "destination": "Imphal"},
    {"id": "Truck-2", "start": "Shillong", "destination": "Imphal"},
    {"id": "Truck-3", "start": "Guwahati", "destination": "Agartala"}
]

print("\nTruck Routes:")

for truck in trucks:
    route = find_route(
        G,
        truck["start"],
        truck["destination"]
    )

    print(
        truck["id"],
        ":",
        route
    )

def is_truck_affected(route, blocked_road):
    for i in range(len(route) - 1):
        road = (route[i], route[i + 1])

        if road == blocked_road or road == blocked_road[::-1]:
            return True

    return False

blocked_road = ("Silchar", "Aizawl")

print("\nAffected Trucks:")

for truck in trucks:
    route = find_route(
        G,
        truck["start"],
        truck["destination"]
    )

    if is_truck_affected(route, blocked_road):
        print(truck["id"], "is affected")
    else:
        print(truck["id"], "is not affected")

print("\nUpdated Truck Routes:")

temp_graph = G.copy()
temp_graph.remove_edge("Silchar", "Aizawl")

for truck in trucks:
    original_route = find_route(
        G,
        truck["start"],
        truck["destination"]
    )

    if is_truck_affected(original_route, ("Silchar", "Aizawl")):
        new_route = find_route(
            temp_graph,
            truck["start"],
            truck["destination"]
        )

        distance, time, risk = route_details(
            temp_graph,
            new_route
        )

        print(truck["id"], "→ Rerouted:", new_route)
        print("   Distance:", distance, "km")
        print("   Time:", time, "minutes")
        print("   Risk:", risk) 
    else:
        distance, time, risk = route_details(G, original_route)

        print(truck["id"], "→ No change:", original_route)
        print("   Distance:", distance, "km")
        print("   Time:", time, "minutes")
        print("   Risk:", risk)

