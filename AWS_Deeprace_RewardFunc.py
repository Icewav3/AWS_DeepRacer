def reward_function(params) :
    all_wheels_on_track = params['all_wheels_on_track']
    speed = params['speed']
    x = params['x']
    y = params['y']
    progress = params['progress']
    is_left_of_center = params['is_left_of_center']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    reverse = params['is_reversed']
    off_track = params['is_offtrack']
    heading = params['heading']
    track_width = params['track_width']
    track_length = params['track_length']
    distance_from_center = params['distance_from_center']
    steps = params['steps']
    steering_angle = params['steering_angle']

    if init == False: #update only once
        center_track = track_width/2
        init = True
    reward = 0 #reset
    reward += all_wheels_on_track
    reward -= off_track
    reward -= distance_from_center
    reward -= reverse
    reward += progress * 100 #as track completes increase reward - could scale by large amount to make car speed up?
    reward += speed > 1 #prevent it from not moving and learning
    
    
    
    return float(reward)