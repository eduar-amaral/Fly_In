*This project has been created as part of the 42 curriculum by eamaral-.*

# Fly-in Drones

## Description

Fly-in Drones is a graph-based map simulation project. The program loads a custom map file, validates its structure, builds a graph, computes routes between hubs, and simulates multiple drones moving simultaneously while respecting the rules of capacity, occupancy, and traffic constraints.

The project is built around a few core ideas:

- parse a custom textual map format
- represent the map as a weighted graph
- compute shortest valid routes
- simulate drones turn by turn
- visualize the result in terminal mode or with pygame

---

## Project structure

| Area | Purpose |
| --- | --- |
| `algorithms/` | graph search logic and shortest-path implementation |
| `graph/` | graph model, heap, nodes and edges |
| `models/` | domain objects such as zones, connections, drones and parsed map data |
| `parser/` | parsing, validation and metadata extraction |
| `pathfinding/` | route computation and search result handling |
| `simulation/` | scheduler, simulation state and turn resolution |
| `ui/` | menus, pygame rendering and terminal rendering |
| `maps/` | map files used by the simulator |

---

## Map format

Each map file follows a custom subject-specific syntax. The parser reads the file and validates the rules before building the graph.

### Basic structure

```text
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: route_a 1 0 [color=blue]
hub: route_b 2 0 [color=yellow]
end_hub: goal 3 0 [color=red]

connection: start-route_a
connection: route_a-route_b
connection: route_b-goal
```

### Supported zone declarations

| Declaration | Meaning |
| --- | --- |
| `start_hub:` | start node of the route |
| `end_hub:` | destination node |
| `hub:` | intermediate node |

Each zone may optionally carry metadata such as:

- `color=...`
- `zone=normal|restricted|priority|blocked`
- `max_drones=<positive integer>`

### Connection declaration

```text
connection: A-B [max_link_capacity=2]
```

A connection links two previously declared zones and may define a maximum number of drones that can use that link in the same turn.

---

## Rules enforced by the parser

The parser validates several rules before the simulation starts:

- first line must be `nb_drones: <positive integer>`
- exactly one start hub is required
- exactly one end hub is required
- zone names must be unique
- connections cannot reference undefined zones
- duplicate connections are rejected
- self-loops are rejected
- metadata must respect the `key=value` format
- zero or negative capacities are rejected

This validation is important because malformed maps must fail before the simulation starts, instead of creating broken runtime states.

---

## Graph model

The project represents the map as a weighted undirected graph:

- zones are nodes
- connections are edges
- each edge carries a cost and capacity
- direction is not used as the main graph primitive, because the simulation is based on bidirectional movement through the map

The graph layer is responsible for:

- registering zones
- attaching edges between connected nodes
- determining the start and end hubs
- building the route graph from the parsed map model

---

## Algorithm strategy

The route search uses Dijkstra's algorithm.

### Why Dijkstra

Dijkstra is appropriate because the graph is weighted and the goal is to find the shortest path from the start to the end while considering the movement cost associated with each zone type.

### Path resolution

The pathfinder receives the graph and computes shortest distances from a start zone. Once distances are known, the system reconstructs the path to the target zone.

### Important cost model

Zone types influence movement cost:

| Zone type | Meaning | Cost |
| --- | --- | --- |
| `normal` | standard traversable zone | 1 |
| `restricted` | slower or constrained zone | 2 |
| `priority` | preferred route | 1 |
| `blocked` | impassable | effectively not traversable |

This means the algorithm does not only consider topology; it also respects traversal cost induced by map rules.

---

## Simulation logic

After the graph is built and the shortest path is known, the simulator creates one drone per requested drone count.

At each turn:

1. current drone positions are read
2. the next target zone is extracted from the path
3. candidate moves are collected
4. zone conflicts are checked
5. link capacity conflicts are checked
6. only safe moves are accepted
7. rejected drones remain in place
8. turn count advances

This is the core scheduler logic. It tries to maximize valid movement while respecting concurrency constraints.

### Capacity rules

The scheduler checks two main constraints:

- zone capacity: a destination zone cannot exceed its `max_drones` limit
- connection capacity: a link cannot exceed its `max_link_capacity` limit

If a move would violate either rule, the drone waits and is recorded as rejected for that turn.

---

## Output format

The project emits simulation results in the standardized subject format.

Example:

```text
D1-route_a
D1-route_b D2-route_a
D1-goal D2-route_b
```

This output format is used to represent the state of all drones turn by turn and is directly aligned with the project conditions.

---

## Execution

### Install dependencies

```bash
make install
```

### Run the project

```bash
make run
```

### Run a map directly in the terminal

```bash
python main.py maps/easy/01_linear_path.txt
```

You can also use the explicit argument form:

```bash
python main.py maps/easy/01_linear_path.txt
```

This bypasses the pygame interface and executes the simulation in terminal mode.

### Lint and static checks

```bash
make lint
```

### Direct execution without Make

```bash
python main.py
```

---

## Visual interface

The project includes a pygame renderer that displays:

- the map
- zones and their colors
- graph connections
- drone positions
- turn history log
- result screen flow

This is useful for debugging and demonstration because it exposes the real routing and scheduling decisions in a visual way.

The terminal renderer is also available for a lighter execution mode and is useful for validation when the graphical interface is not needed.

---

## Validation and quality checks

The project is validated through:

- `flake8` for style and syntax checks
- `mypy` for static type validation

This keeps the codebase more predictable and reduces the chance of runtime failures caused by bad assumptions or broken interfaces.

---

## Notes

The project is intentionally structured so that each layer has a clear responsibility:

- parser validates input
- graph stores the map topology
- pathfinding computes routes
- scheduler resolves simultaneous movement conflicts
- renderer displays the result

That separation is one of the key strengths of the implementation and makes the code easier to extend without breaking the whole system.

---

## Summary

This project is a complete graph-based routing and simulation system with:

- strict parsing and validation
- weighted shortest-path search
- multi-drone scheduling under capacity constraints
- terminal and graphical execution modes
- test coverage for common and edge-case scenarios

It is designed to be both practical and educational, while staying close to the original project rules and constraints.
