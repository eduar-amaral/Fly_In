*This project has been created as part of the 42 curriculum by <login1>.*

# Fly-in Drones

## Description

Fly-in Drones is a graph-based simulation project in which multiple drones must move through a map from a start hub to an end hub while respecting zone capacities, connection constraints, and movement costs. The project includes a parser for custom map files, an optimization-oriented pathfinding layer, and a visual simulation interface.

The goal is to route all drones efficiently, minimize turn count, and respect the rules defined in the project statement. The simulation can be run either in terminal mode or in a graphical pygame window, making it useful both for debugging and for demonstration.

## Instructions

### Requirements

- Python 3.11+
- pip
- pygame

Install dependencies and create the virtual environment:

```bash
make install
```

Run the project:

```bash
make run
```

Run the tests:

```bash
make test
```

Run lint and type checks:

```bash
make lint
```

Run everything together:

```bash
make check
```

Or run directly without make:

```bash
python main.py
```

## Algorithm strategy

The implementation uses a graph representation where zones are nodes and connections are edges. Each zone carries metadata such as capacity, movement type, and color information. The parser validates the custom subject format and converts map files into a structured object model.

The pathfinding layer relies on Dijkstra-based shortest-path search to compute valid routes between the start and destination hubs. During the simulation, each drone advances according to the graph route while the scheduler checks occupancy, conflicts, and capacity constraints. The simulation records one movement line per turn in the required subject format.

## Visual representation

The project includes a graphical renderer built with pygame. It displays the map, zones, edges, and drones in real time. The interface allows the user to inspect the simulation visually and review the historical log of movement actions. This helps with debugging, validation, and demonstration of the routing result.

The terminal view also prints the simulation events in a compact, readable format for quick verification.

## Example input and expected output

Example map snippet:

```text
2
start_hub: start 0 0
hub: waypoint1 1 0
hub: waypoint2 2 0
end_hub: goal 3 0
connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

Example output:

```text
D1-waypoint1 D2-waypoint1
D1-waypoint2 D2-waypoint2
D1-goal D2-goal
```

## Resources

The project relies on classic graph-search and pathfinding concepts, especially:

- Dijkstra's algorithm
- shortest-path optimization
- graph traversal and occupancy validation
- simulation scheduling and turn-based routing

Relevant references include:

- Python documentation
- pygame documentation
- graph algorithm tutorials and shortest-path explanation articles
- project subject documentation for map rules and output format

AI usage:

- Used to review import structure and remove circular dependencies
- Used to help validate the simulation output format against the project statement
- Used to assist with UI debugging and scroll behavior in the history panel

## Notes

This project is designed to be extensible. It is straightforward to add new maps, tweak simulation rules, or improve the visual representation while keeping the core graph and scheduling logic stable.
