import math
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
    
    
    # Penalize for off-track, crash, or reverse
    if not all_wheels_on_track or reversed or off_track or crashed:
        reward += 1e-3 
    
    
    # Follow center line
    
    # Calculate 3 markers that are at varying distances away from the center line
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width
    
    # Give higher reward if the car is closer to center line and vice versa
    if distance_from_center <= marker_1:
        reward += 1.0
    elif distance_from_center <= marker_2:
        reward += 0.5
    elif distance_from_center <= marker_3:
        reward += 0.1
    else:
        reward += 1e-3  # likely crashed/ close to off track
    

    # Using waypoints
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]

    # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
    track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
    # Convert to degree
    track_direction = math.degrees(track_direction)

    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    # Penalize the reward if the difference is too large
    DIRECTION_THRESHOLD = 10.0
    if direction_diff > DIRECTION_THRESHOLD:
        reward *= 0.5


    # All wheels on track 

    # Set the speed threshold based your action space
    SPEED_THRESHOLD = 1.0

    if not all_wheels_on_track:
        # Penalize if the car goes off track
        reward += 1e-3
    elif speed < SPEED_THRESHOLD:
        # Penalize if the car goes too slow
        reward += 0.5
    else:
        # High reward if the car stays on track and goes fast
        reward += 1.0

    
    # Steering

    # Read input variable
    abs_steering = abs(params['steering_angle'])

    # Penalize if car steer too much to prevent zigzag
    ABS_STEERING_THRESHOLD = 35.0
    if abs_steering > ABS_STEERING_THRESHOLD:
        reward *= 0.8


    # Steps 

    # Total num of steps we want the car to finish the lap, it will vary depends on the track length
    TOTAL_NUM_STEPS = 300

    # Give additional reward if the car pass every 100 steps faster than expected
    if (steps % 100) == 0 and progress > (steps / TOTAL_NUM_STEPS) * 100 :
        reward += 10.0


    # Track width

    # Calculate the distance from each border
    distance_from_border = 0.5 * track_width - distance_from_center

    # Reward higher if the car stays inside the track borders
    if distance_from_border >= 0.05:
        reward += 1.0
    else:
        reward += 1e-3 # Low reward if too close to the border or goes off the track

    # Normalize the reward to be between 0 and 1
    reward = max(min(reward, 1.0), 0.0)

    return float(reward)
