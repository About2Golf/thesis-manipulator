## @file mainpage.py
#  @authors {Thomas Goehring, Jason Grillo, Trent Peterson}
#  @mainpage
#  @section intro Introduction
#  @subsection purpose Purpose
#  This software is intended to control a turret with pan and tilt functionality. A user interface will communicate with the board to give commands. The board runs the cotask rtos which implements the timing for each of out tasks.
#  @subsection usage Usage
#  This scheduler runs an IMU, an encoder, two motors, and nerf gun motor drive, and a mastermind hub simultaneously using a cotask class. The motors and encoders are run through a user interface that just needs any key to be pressed. The motor, encoder, and IMU task function are used to control each task.
#  @subsection testing Testing
#  Extensive Testing was performed on the design
#  @subsection bugs Bugs_&_Limitations
#  Software wise there are no known bugs. Mechanically there is an issue with setscrew gear/shaft slip of the pan axis. 
#  @subsection location Location_of_Source_Code
#  http://wind.calpoly.edu/hg/mecha10
