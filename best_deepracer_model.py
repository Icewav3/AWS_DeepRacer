import math

# Creating a function to calculate distance between two points.
def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

# Creating a function to calculate curvature of the track.
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

# Creating the main reward function.
def reward_function(params) :
    # Declaring all the parameters required.
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
    
    
    # Penalizing for off-track, crash, or reverse.
    if not all_wheels_on_track or reverse or off_track or crashed:
        reward += 1e-3 
    
    # Making sure the model follows center line.
    # Calculating 3 markers that are at varying distances away from the center line.
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

    # Giving higher reward if the car is closer to center line and vice versa
    # Based on distance from center the reward is being appended.
    if distance_from_center <= marker_1:
        reward += 1.0
    elif distance_from_center <= marker_2:
        reward += 0.5
    elif distance_from_center <= marker_3:
        reward += 0.1
    else:
        reward += 1e-3  # likely crashed/ close to off track

    # Making sure the model is staying on track and receives reward accordingly.
    if all_wheels_on_track and (0.5*track_width - distance_from_center) >= 0.05:
        reward += 1.0
    else:
        reward += 1e-3

    # Using waypoints
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]

    # Calculating the direction of model in radius and converting in degrees.
    track_direction = math.degrees(math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0]))

    # Calculating the difference between the track direction and the heading direction of the car.
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    # Penalizing the reward if the difference is too large.
    DIRECTION_THRESHOLD = 10.0
    if direction_diff > DIRECTION_THRESHOLD:
        reward *= 0.5

    # Setting the speed threshold based your action space.
    SPEED_THRESHOLD = 1.0

    # Making sure the model's all wheels are on track. 
    # Also, if the model is on track then checking the speed of it.
    if not all_wheels_on_track:
        # Penalizing if the car goes off track.
        reward += 1e-3
    # If the model is on track, then the model should be fast.
    elif speed < SPEED_THRESHOLD:
        # Penalizing if the car goes too slow.
        reward += 0.5
    else:
        # High reward if the car stays on track and goes fast.
        reward += 1.0

    prev_wp, next_wp = closest_waypoints

    # Speed management based on curvature.
    # Calculating the curvature of the next track segment and adjusting speed reward.
    pointA, pointB = waypoints[prev_wp], waypoints[next_wp]
    pointC = waypoints[next_wp + 1] if next_wp + 1 < len(waypoints) else waypoints[0]  # Loop back if at end
    next_curve = calculate_curve(pointA, pointB, pointC)
    
    # Declaring the optimal speed of model based on angle.
    optimal_speed = 0.8 if next_curve > 60 else 1.5
    reward += speed / optimal_speed

    # Using is_left_of_center.
    # Function to check how much heading of model needs to be changed.
    def calculate_heading_change(current_heading, next_waypoint, current_position):
        dx = next_waypoint[0] - current_position[0]
        dy = next_waypoint[1] - current_position[1]
        desired_heading = math.degrees(math.atan2(dy, dx))
        angle_change = desired_heading - current_heading
        # Normalize to -180 to 180
        angle_change = (angle_change + 180) % 360 - 180
        return angle_change

    # Function to determine if the next turn is left or right
    def is_next_turn_left(current_heading, next_waypoint, current_position):
        angle_change = calculate_heading_change(current_heading, next_waypoint, current_position)
        return angle_change < 0  # Negative angle change indicates a left turn

    # Checking current position of the model.
    current_position = (x,y)
    
    next_waypoint_index = closest_waypoints[1]
    next_waypoint = waypoints[next_waypoint_index]

    # Checking if the next turn is left or not.
    next_turn_is_left = is_next_turn_left(heading, next_waypoint, current_position)

    # Giving rewards based on the following conditions.
    if next_turn_is_left:
        if not is_left_of_center:
            reward += 1.0  # Reward being on the right if the next turn is left.
        else:
            reward += 0.5  # Lesser reward for not being optimally positioned.
    else:  # Over here the next turn is right.
        if is_left_of_center:
            reward += 1.0  # Reward being on the left if the next turn is right
        else:
            reward += 0.5  # Lesser reward for not being optimally positioned
   
    # Steering
    # Read input variable and making sure it is an absolute value.
    abs_steering = abs(steering_angle)

    # Penalizing if car steer too much to prevent zigzag.
    ABS_STEERING_THRESHOLD = 20.0
    if abs_steering > ABS_STEERING_THRESHOLD:
        reward *= 0.8

    # Track width
    # Calculating the distance from each border.
    distance_from_border = 0.5 * track_width - distance_from_center

    # Rewarding higher if the car stays inside the track borders.
    if distance_from_border >= 0.10:
        reward += 1.0
    else:
        reward += 1e-3 # Low reward if too close to the border or goes off the track.

    # Normaliziing the reward to be between 0 and 1.
    reward = max(min(reward, 1.0), 0.0)

    # Returning the reward.
    return float(reward)
