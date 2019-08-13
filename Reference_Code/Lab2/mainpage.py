## @file mainpage.py
#  @authors {Thomas Goehring, Jason Grillo, Trent Peterson}
#  @mainpage
#  @section intro Introduction
#  @subsection purpose Purpose
#  The controller driver's purpose is to interface with the ME 405 Nucleo board to provide a generic porportional gain controller.
#  @subsection usage Usage
#  The controller class is used to create a controller object. Once a controller object is created, the user can set setpoints position values, Kp values, and run the porportional control algorithm to get a PWM actuation signal.
#  @subsection testing Testing
#  The controller driver was tested by running the code in the main file. We created a setup and loop function. The setup function zeroed the encoder and set the motor duty cycle to zero. The loop function runs a while loop for a user selected amount of loops performing the porportional control algorithm to get a duty cycle and then setting the duty cycle to the motor each time. To run our testing we created a motor, encoder and controller object with the appropriate parameters. We ran the setup() function, and then the loop() function. Running this in the putty terminal, we watched the feed back of the encoder with respect to time. The controller was tested at different setpoints and Kp values.
#  @subsection bugs Bugs_&_Limitations
#  There are no known bugs in the driver after the current testing. 
#  @subsection location Location_of_Source_Code
#  http://wind.calpoly.edu/hg/mecha10
