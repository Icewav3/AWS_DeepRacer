
def reward_function(params) :
    reward = 0
    all_wheels_on_track = params['all_wheels_on_track']
    speed = params['speed']
    x = params['x']
    y = params['y']
    is_left_of_center = params['is_left_of_center']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    crashed = params['is_crashed']
    reverse = params['is_reversed']
    off_track = params['is_offtrack']
    heading = params['heading']
    track_width = params['track_width']
    track_length = params['track_length']
    distance_from_center = params['distance_from_center']
    steps = params['steps']
    progress = params['progress']
    steering_angle = params['steering_angle']
    
    
    reward += 1

    return float(reward)