import numpy as np

# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function

countRobotIsStuck = 0
previousAngle = 0

def checkIfStuck(Rover):
    global countRobotIsStuck
    global previousAngle
    # This function always check if the rover gets stuck, if it does, it would always need to get out first by doing a turn
    meanAngle = np.mean(Rover.nav_angles * 180/np.pi)
    if Rover.vel < 0.05 and (abs(meanAngle - previousAngle) < 2) and Rover.mode != 'stop' and not Rover.picking_up:
        print('may be stuck ', Rover.vel)
        countRobotIsStuck += 1
    else:
        countRobotIsStuck = 0
    
    previousAngle = meanAngle
    
    if countRobotIsStuck > 20:
        print('It probably is stuck')
        Rover.throttle = 0
        # Release the brake to allow turning
        Rover.brake = 10
        # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
        Rover.steer = -15 # Could be more clever here about which way to turn
        countRobotIsStuck = 0
    return Rover

def decision_step(Rover):
    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!
    
    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward': 
            print('forward:', len(Rover.nav_angles))
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                # TODO: is it possible to refine this
                steering_deg = np.mean(Rover.nav_angles * 180/np.pi)
                Rover.steer = np.clip(steering_deg, -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                # Set mode to "stop" and hit the brakes!
                Rover.throttle = 0
                # Set brake to stored brake value
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'
                    
            # TODO: update to elif if necessary
            
            if Rover.samples_seen_yet_pickup:
                print('change to slow mode')
                Rover.mode = 'slow'
                Rover.throttle = 0
                # Release the brake to allow turning
                Rover.brake = 0
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            print('stop:', len(Rover.nav_angles))
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                    
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
        
        # If we're already in "slow" mode then it means there is a rock nearby and should inch closer
        # An extra mode, so we do not clash with forward
        elif Rover.mode == 'slow':
            print('slow:', len(Rover.nav_angles))
            if len(Rover.nav_angles) >= 1: 
                if not Rover.samples_seen_yet_pickup:
                    Rover.mode = 'forward'
                
                Rover.throttle = Rover.throttle_set
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                
                if Rover.vel > Rover.max_vel /2:
                    Rover.throttle = 0
                    
                if Rover.near_sample:
                    Rover.throttle = 0
                    Rover.brake = 10
                    
            else:
                Rover.throttle = 0
                # Release the brake to allow turning
                Rover.brake = 0
                # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                Rover.steer = -15 # Could be more clever here about which way to turn
                    
        # Always check if stuck in all method
        Rover = checkIfStuck(Rover)
                    
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
        
        
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        print('Pick up rock')
        Rover.send_pickup = True
    
    elif Rover.near_sample and not Rover.picking_up:
        print('Set vel to 0 as near sample')
        Rover.vel = 0 
    
    
    return Rover

