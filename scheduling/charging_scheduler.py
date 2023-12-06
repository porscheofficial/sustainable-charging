def get_time_to_charge(
    battery_capacity: float,
    charging_curve: list[float],
    current_soc: int,
    target_soc: int = 80,
    efficiency: float = 0.9,
) -> float:
    """
    Get the estimated time to charge from the current state of charge (SOC) to a target SOC.

    Args:
        battery_capacity: The capacity of the battery
        charging_curve: The charging curve of the battery
        current_soc: The current state of charge (between 0 and 100)
        target_soc: The target state of charge (between 0 and 100, defaults to 80)
        efficiency: The efficiency of the charging process (between 0 and 1, defaults to 0.9)

    Returns:
        The estimated time to charge in h
    """

    one_percent_capacity = battery_capacity / 100
    charging_rates = zip(
        charging_curve[current_soc:target_soc],
        charging_curve[current_soc + 1 : target_soc + 1],
    )

    return (
        sum(
            2 * one_percent_capacity / (current_rate + next_rate)
            for (current_rate, next_rate) in charging_rates
        )
        / efficiency
    )
