import math

def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def calculate_curve(pointA, pointB, pointC):
    a = calculate_distance(pointB, pointC)
    b = calculate_distance(pointA, pointC)
    c = calculate_distance(pointA, pointB)
    s = (a + b + c) / 2
    area = math.sqrt(s * (s - a) * (s - b) * (s - c))
    if area == 0:
        return 0
    R = (a * b * c) / (4 * area)
    return 1 / R

def reward_function(params) :
    reward = 1
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
    if not all_wheels_on_track or reverse or off_track or crashed:
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

    # Staying on track
    if all_wheels_on_track and (0.5*track_width - distance_from_center) >= 0.05:
        reward += 1.0
    else:
        reward += 1e-3

    # Using waypoints
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]

    # Calculate the direction in radius and convert in degrees.
    track_direction = math.degrees(math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0]))

    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    # Penalize the reward if the difference is too large
    DIRECTION_THRESHOLD = 10.0
    if direction_diff > DIRECTION_THRESHOLD:
        reward *= 0.5

    # All wheels on track 

    # Set the speed threshold based on our action space
    SPEED_THRESHOLD = 1.5

    if not all_wheels_on_track:
        # Penalize if the car goes off track
        reward += 1e-3
    elif speed < SPEED_THRESHOLD:
        # Penalize if the car goes too slow
        reward += 0.5
    else:
        # High reward if the car stays on track and goes fast
        reward += 1.0

    prev_wp, next_wp = closest_waypoints

    # Speed management based on curvature
    # Calculate the curvature of the next track segment and adjust speed reward
    pointA, pointB = waypoints[prev_wp], waypoints[next_wp]
    pointC = waypoints[next_wp + 1] if next_wp + 1 < len(waypoints) else waypoints[0]  # Loop back if at end
    next_curve = calculate_curve(pointA, pointB, pointC)
    optimal_speed = 0.8 if next_curve > 60 else 1.5
    reward += speed / optimal_speed

    # Using is_left_of_center
    # Function to determine if the next turn is left or right
    def calculate_heading_change(current_heading, next_waypoint, current_position):
        dx = next_waypoint[0] - current_position[0]
        dy = next_waypoint[1] - current_position[1]
        desired_heading = math.degrees(math.atan2(dy, dx))
        angle_change = desired_heading - current_heading
        # Normalize to -180 to 180
        angle_change = (angle_change + 180) % 360 - 180
        return angle_change

    def is_next_turn_left(current_heading, next_waypoint, current_position):
        angle_change = calculate_heading_change(current_heading, next_waypoint, current_position)
        return angle_change < 0  # Negative angle change indicates a left turn

    current_position = (x,y)
    
    next_waypoint_index = closest_waypoints[1]
    next_waypoint = waypoints[next_waypoint_index]

    next_turn_is_left = is_next_turn_left(heading, next_waypoint, current_position)

    if next_turn_is_left:
        if not is_left_of_center:
            reward += 1.0  # Reward being on the right if the next turn is left
        else:
            reward += 0.5  # Lesser reward for not being optimally positioned
    else:
        if is_left_of_center:
            reward += 1.0  # Reward being on the left if the next turn is right
        else:
            reward += 0.5  # Lesser reward for not being optimally positioned
    
    # Speed management on straight path
    STRAIGHT_PATH_THRESHOLD = 10
    ABS_STEERING_THRESHOLD = 20.0

    def calculate_heading_change_st(wp1, wp2, wp3):
        # Placeholder logic for calculating heading change
        dx1, dy1 = wp2[0] - wp1[0], wp2[1] - wp1[1]
        dx2, dy2 = wp3[0] - wp2[0], wp3[1] - wp2[1]
        angle1 = math.atan2(dy1, dx1)
        angle2 = math.atan2(dy2, dx2)
        angle_change_st = math.degrees(angle2 - angle1)
        return abs(angle_change_st)  

    def is_straight_path(waypoints, closest_waypoints, lookahead=5):
        current_index = closest_waypoints[1]  # index of the waypoint just after the vehicle
        
        # Ensure we don't go out of bounds by adjusting the lookahead if necessary
        max_index = min(current_index + lookahead, len(waypoints) - 2)
        
        total_angle_change = 0
        for i in range(current_index, max_index):
            # Calculate the angle change between three consecutive waypoints
            angle_change_st = calculate_heading_change_st(waypoints[i], waypoints[i + 1], waypoints[i + 2])
            total_angle_change += abs(angle_change_st)
        
        # Consider the path straight if the total angle change is minimal
        return total_angle_change < STRAIGHT_PATH_THRESHOLD
    
    # Reward for maintaining high speed on straight paths
    if is_straight_path(waypoints, closest_waypoints):
        if speed > SPEED_THRESHOLD:  # Encourage maintaining high speed on straight paths
            reward += 1.25
        else:
            reward += 0.75  # Still on a straight path but not at optimal speed
    else:
        # Handling curves
        if abs(steering_angle) < ABS_STEERING_THRESHOLD and speed < optimal_speed:
            reward += 0.75  # Reward for smooth and controlled handling of curves
        else:
            reward += 0.5

    # Steering

    # Read input variable
    abs_steering = abs(steering_angle)

    # Penalize if car steer too much to prevent zigzag
    if abs_steering > ABS_STEERING_THRESHOLD:
        reward *= 0.5

    # Track width

    # Calculate the distance from each border
    distance_from_border = 0.5 * track_width - distance_from_center

    # Reward higher if the car stays inside the track borders
    if distance_from_border >= 0.10:
        reward += 1.0
    else:
        reward += 1e-3 # Low reward if too close to the border or goes off the track

    # Normalize the reward to be between 0 and 1
    reward = max(min(reward, 1.0), 0.0)

    return float(reward)
