def average_sensor_readings(readings_list):
    """
    Takes a list of sensor reading dictionaries and averages the metrics
    for each sensor over time. Keeps each sensor's data isolated.
    """
    if not readings_list:
        return {}

    # 1. Set up a blank dictionary based on the first reading's structure
    first_reading = readings_list[0]
    averages = {}

    for sensor_id, metrics in first_reading.items():
        # Create a zeroed-out dictionary for each metric
        averages[sensor_id] = {metric_name: 0.0 for metric_name in metrics}

    num_readings = len(readings_list)

    # 2. Add up all the values from every reading in the list
    for reading in readings_list:
        for sensor_id, metrics in reading.items():
            for metric_name, value in metrics.items():
                averages[sensor_id][metric_name] += value

    # 3. Divide by the total number of readings to get the average
    for sensor_id, metrics in averages.items():
        for metric_name in metrics:
            averages[sensor_id][metric_name] /= num_readings

    return averages