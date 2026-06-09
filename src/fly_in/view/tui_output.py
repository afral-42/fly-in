from fly_in.services.pathfinder import Position


def print_output(positions: list[list[Position]], start: str) -> None:
    """Print step-by-step drone movements according to constraints.

    Iterates through time steps and prints movements for each drone
    when its hub changes relative to the previous turn. Flight nodes
    that represent physical connections are printed using the
    connection endpoints.

    Args:
        positions: A list where each element is a drone path (a list
            of `Position` objects) representing the drone route per
            time step.
        start: The name of the starting hub used as the initial
            previous position for all drones.

    Returns:
        None. Output is written to standard output.
    """
    if not positions:
        return

    max_turns = max(len(path) for path in positions)

    prev_positions: dict[int, str] = {i: start for i in range(len(positions))}

    for turn in range(max_turns):
        turn_movements: list[str] = []

        for i, drone_path in enumerate(positions):
            drone_id = i + 1

            if turn < len(drone_path):
                next_node = drone_path[turn]
                if prev_positions[i] != next_node.hub_name:
                    if (
                        next_node.is_flight_node
                        and next_node.physical_connection
                    ):
                        conn_start, conn_end = next_node.physical_connection
                        turn_movements.append(
                            f"D{drone_id}-{conn_start}-{conn_end}"
                        )
                    else:
                        turn_movements.append(
                            f"D{drone_id}-{next_node.hub_name}"
                        )

                    prev_positions[i] = next_node.hub_name

        if turn_movements:
            print(" ".join(turn_movements))
