from __future__ import annotations

from graph import Graph
from models import Drone

from .simulation_state import SimulationState
from .step_result import Movement, StepResult, Wait


class Scheduler:
    """Resolve one turn of the simulation by validating drone moves."""

    def __init__(self, graph: Graph) -> None:
        """Create a scheduler bound to a graph.

        Args:
            graph: Graph used to validate zone and link capacity.
        """
        self._graph = graph

    def step(self, state: SimulationState) -> StepResult:
        """Advance the simulation by one turn.

        Args:
            state: Current simulation state.

        Returns:
            Result describing all movements and waits for the turn.
        """
        active_drones = [
            drone
            for drone in state.drones
            if not drone.finished
        ]

        result = StepResult()

        ready_drones = []
        for drone in active_drones:
            if drone.wait_turns > 0:
                if drone.consume_wait():
                    result.waits.append(
                        Wait(
                            drone_id=drone.drone_id,
                            zone=drone.current_zone,
                            reason="restricted zone",
                        )
                    )
                continue

            ready_drones.append(drone)

        candidates = self._build_candidates(ready_drones)

        accepted, rejected = self._resolve_moves(
            ready_drones,
            candidates,
        )

        for drone in ready_drones:
            decision = candidates.get(drone.drone_id)

            if decision is None:
                continue

            from_zone, to_zone = decision

            if drone.drone_id in accepted:
                result.movements.append(
                    Movement(
                        drone_id=drone.drone_id,
                        from_zone=from_zone,
                        to_zone=to_zone,
                    )
                )
            else:
                result.waits.append(
                    Wait(
                        drone_id=drone.drone_id,
                        zone=from_zone,
                        reason=rejected.get(
                            drone.drone_id,
                            "blocked",
                        ),
                    )
                )

        for drone in ready_drones:
            if drone.drone_id in accepted:
                drone.move()
                target_zone = self._graph.get_zone(drone.current_zone)
                if target_zone.movement_cost > 1:
                    drone.wait(target_zone.movement_cost - 1)

        state.turn += 1

        return result

    def _build_candidates(
        self,
        drones: list[Drone],
    ) -> dict[int, tuple[str, str]]:
        """Map each drone to its next planned move when it is not finished."""
        candidates: dict[int, tuple[str, str]] = {}

        for drone in drones:
            next_zone = drone.next_zone()

            if next_zone is None:
                continue

            candidates[drone.drone_id] = (
                drone.current_zone,
                next_zone,
            )

        return candidates

    def _resolve_moves(
        self,
        drones: list[Drone],
        candidates: dict[int, tuple[str, str]],
    ) -> tuple[set[int], dict[int, str]]:
        """Resolve conflicts and return accepted drones with reasons."""
        accepted = set(candidates)
        rejected: dict[int, str] = {}

        while True:
            conflicts = self._find_zone_conflicts(
                drones,
                candidates,
                accepted,
            )

            link_conflicts = self._find_link_conflicts(
                candidates,
                accepted,
            )

            changed = False

            for drone_ids in conflicts:
                for drone_id in drone_ids:
                    if drone_id in accepted:
                        accepted.remove(drone_id)
                        rejected[drone_id] = "zone full"
                        changed = True

            for drone_ids in link_conflicts:
                for drone_id in drone_ids:
                    if drone_id in accepted:
                        accepted.remove(drone_id)
                        rejected[drone_id] = "link full"
                        changed = True

            if not changed:
                break

        return accepted, rejected

    def _find_zone_conflicts(
        self,
        drones: list[Drone],
        candidates: dict[int, tuple[str, str]],
        accepted: set[int],
    ) -> list[list[int]]:
        """Return groups of drones that exceed a zone capacity."""
        occupancy = self._get_final_occupancy(
            drones,
            candidates,
            accepted,
        )

        conflicts: list[list[int]] = []

        for zone in self._graph.all_zones():
            # The start hub may initially contain all drones.
            if zone.is_start:
                continue

            current_occupancy = occupancy.get(zone.name, 0)

            overflow = current_occupancy - zone.max_drones

            if overflow <= 0:
                continue

            incoming = sorted(
                (
                    drone_id
                    for drone_id in accepted
                    if candidates[drone_id][1] == zone.name
                ),
                reverse=True,
            )

            if incoming:
                conflicts.append(incoming[:overflow])

        return conflicts

    def _find_link_conflicts(
        self,
        candidates: dict[int, tuple[str, str]],
        accepted: set[int],
    ) -> list[list[int]]:
        """Return groups of drones competing for the same edge capacity."""
        link_usage: dict[frozenset[str], list[int]] = {}

        for drone_id in accepted:
            from_zone, to_zone = candidates[drone_id]

            link = frozenset((from_zone, to_zone))

            link_usage.setdefault(link, []).append(drone_id)

        conflicts: list[list[int]] = []

        for link, drone_ids in link_usage.items():
            from_zone, to_zone = candidates[drone_ids[0]]

            edge = self._graph.get_edge(
                from_zone,
                to_zone,
            )

            overflow = len(drone_ids) - edge.capacity

            if overflow > 0:
                conflicts.append(
                    sorted(drone_ids, reverse=True)[:overflow]
                )

        return conflicts

    def _get_final_occupancy(
        self,
        drones: list[Drone],
        candidates: dict[int, tuple[str, str]],
        accepted: set[int],
    ) -> dict[str, int]:
        """Compute occupancy after all accepted moves are applied."""
        occupancy: dict[str, int] = {}

        # Finished drones do not occupy zones.
        for drone in drones:
            zone_name = drone.current_zone

            occupancy[zone_name] = (
                occupancy.get(zone_name, 0) + 1
            )

        # Calculate the occupancy after all accepted moves.
        for drone_id in accepted:
            from_zone, to_zone = candidates[drone_id]

            occupancy[from_zone] -= 1
            occupancy[to_zone] = (
                occupancy.get(to_zone, 0) + 1
            )

        return occupancy
