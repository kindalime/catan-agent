def counter_to_list(data):
    return [val for val, cnt in data for i in range(cnt)]

def max_values_dict(data):
    max_value = max(data.values())
    return [k for k,v in data.items() if v == max_value], max_value

player_colors = ["blue", "red", "green", "purple"]
