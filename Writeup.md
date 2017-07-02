## Project: Search and Sample Return
### This project is modeled after the [NASA sample return challenge](https://www.nasa.gov/directorates/spacetech/centennial_challenges/sample_return_robot/index.html). It is created by Udacity for the Robotics Nanodegree course

---

[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./final_rover_image.png
[image3]: ./calibration_images/example_rock1.jpg 


### Solution

#### Settings
Screen resolution: 640 x 480
Graphics quality: Fastest
Machine: Macbook Pro

#### Result
![alt text][image2]
Video: https://youtu.be/n2-_8oubxn4

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points

---

### Notebook Analysis

#### 1. Color thresholding
# Thresholding for rocks
A threshold with a range from RGB(120,100,0) and RGB(180,180,70) is used to detect rocks. This is a range for yellow color
# Thresholding for obstacles
A threshold with a range from RGB(10,10,10) and RGB(80,80,80) is used to detect obstacle. A lower range is used as some part cant be seen by the rover and this returns as black

# Thresholding for ground
A threshold of RGB(180,180,180) as a lower range to detect the ground based on the image

![alt text][image1]

#### 2. Processing image
The process_image function would do the following step to produces a video
* Input: ground truth, image from rover
* Output: Warped image and worldmap
* Process:
1. An image of the path is analysed. 
2. 4 points are taken, consider like a grid, and it is warped. Image warping is the process of digitally manipulating an image such that any shapes portrayed in the image have been significantly distorted [Wikipedia]
3. The image is warped as if the image is taken from above, using a size of 10x10 with an offset of 6 (to accommodate the size of the robot). 
4. The warped image is filtered by applying a threshold for 3 scenarios: navigable route, obstacle and rock
5. Filtered images are rotated to fit the rover coordinates, with positive x at the bottom going right and y going up
6. As the current images represent one portion of the map, a pix_to_world function is used to  fit the part of the image onto the world map
7. The worldmap is 10 times the size of the map (an assumption), a 1/10 scale is used
8. The worldmap is overlayed wtih different color for obstacle, navigable and rock for inspection purposes


#### 2. Processed video
https://github.com/frozenamazon/RoboND-Rover-Project/blob/master/output/test_mapping.mp4


### Autonomous Navigation and Mapping
To allow autonous navigation, there are two parts; perception - how it would perceive and analyse the environment, decision - how it decides to react based on information it has received

#### 1. Perception
The main step in perception is to analyse the rover's image.
1. An image of the path is analysed. 
2. 4 points are taken, consider like a grid, and it is warped. Image warping is the process of digitally manipulating an image such that any shapes portrayed in the image have been significantly distorted [Wikipedia]
3. The image is warped as if the image is taken from above, using a size of 10x10 with an offset of 6 (to accommodate the size of the robot). 
4. The warped image is filtered by applying a threshold for 3 scenarios: navigable route, obstacle and rock
5. Filtered images are rotated to fit the rover coordinates, with positive x at the bottom going right and y going up
6. As the current images represent one portion of the map, a pix_to_world function is used to  fit the part of the image onto the world map
7. The worldmap is 10 times the size of the map (an assumption), a 1/10 scale is used
8. The worldmap is overlayed wtih different color for obstacle, navigable and rock for inspection purposes

After processing the images, it would check the width of the navigable path. If it is a wide path, it would try to stay towards the left, mimicking a wall crawler. If it is a narrow path, it would just take the mean to avoid it from being stuck. It would return four values nav_angles_rock and nav_dists_rock, nav_angles and nav_dists. 

#### 2. Decision
There are four modes
* Forward
Most of the time the rover is in this mode. It would check whether there is a yellow rock nearby. If there is it would update the 'slow' mode to move towards the rock. Else it would move forward according to the navigables until it sees a deadend (minimum amount of navigable)

* Stop
This mode means stop. The rover is stopped for reasons because it is stuck or sees a deadend. It would brake if there is a speed of more than 0.2. Else it would rotate on the spot until it sees a navigable path

* Slow
This mode represents there is a yellow rock and it should try to go slowly towards the yellow rock. It checks whether the yellow rock can still be found, if not it would change back to forward mode and continue the journey. It takes the nav_angles_rock and nav_dists_rock instead of nav_angles and nav_dists. However nav_angles_rock is compared to nav_angles, ensuring that the angle to the yellow rock is within a navigable angle and not through an obstacle

* Stuck
This mode it is usually stuck. It would release the throttle and the brake, allowing it to turn -30. It would switch back to forward mode once it is no longer stuck. The way it decides is to check the yaw when it is stuck compared to the current yaw.



#### Pipeline of failure
1. The rover has some problems navigating around tight areas with plenty of big stones. As it takes the mean of the angles, if the big stones is right in the front with angle of -5deg to 5deg, and with a clear path between it, it would get the mean of these angles and drive straight into it
2. The rover encounters problem it large area where it goes around in circles infinitely
3. Upon collecting yellow rocks, especially those very close to the wall, it takes a while to continue its journey after as it may be stuck
4. Rocks in areas surrounded by big stones causes the rover to get stuck between the big stones. It kinda goes through the stone, sees a nvigable path, failing to detect the obstacles, seeing only blue not red, but it would be able to proceed through
5. Many times it found the yellow rock , closing it to the yellow rock , the rock disappears from the vision

#### Improvements
1. One way which I have not managed to work out is feeding the information back from the worldmap that has been populated from previous data. Anything that has been 'visited' with be blue, [:,:,2] > 0. From the worldmap, it should be possible to create another function that shows the portion of the worldmap, compare it to the current map and decide the navigable (which is any route opposite to what has been visited previously)
2. Realising the rover is going in circle, which is actually stuck
3. Always choosing the left path when it sees a fork, and being able to decide it is a fork


