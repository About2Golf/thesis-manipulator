## @file mainpage.py
#  @authors {Thomas Goehring, Jason Grillo, Trent Peterson}
#  @mainpage
#  @section intro Introduction
#  @subsection purpose Purpose
#  This real time scheduler runs multiple tasks using cooperative multitasking. It schedules tasks in order of their assigned period and priority and runs them accordingly.
#  @subsection usage Usage
#  This scheduler runs two encoders and two motors simultaneously using a cotask class. The motors and encoders are run through a user interface that just needs any key to be pressed. The motor and encoder objects are created and initialized upon reboot and the motor setpoints and Kp value are set within the file. 
#  @subsection testing Testing
#  The scheduler was first tested to verify that both encoders and motors would run simultaneously and independently of each other. Once functionality was verified, the motor control task was run at increasingly slower rates and the motors performance was analyzed using its step response. The motor was slowed until a response difference was seen, marking the upper limit of the period used to control the motor. The motor period was further increased until instability.  
#  @subsection bugs Bugs_&_Limitations
#  There are no known bugs in the driver after the current testing. 
#  @subsection location Location_of_Source_Code
#  http://wind.calpoly.edu/hg/mecha10
