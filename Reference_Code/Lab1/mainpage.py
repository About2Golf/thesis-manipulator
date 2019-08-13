## @file mainpage.py
#  @authors {Thomas Goehring, Jason Grillo, Trent Peterson}
#  @mainpage
#  @section intro Introduction
#  @subsection purpose Purpose
#  The encoder driver's purpose is to interface with the ME 405 Nucleo board to read the position of an encoder.
#  @subsection usage Usage
#  The Encoder class is used to create an encoder object. Once an encoder object is created, the user can get the position of the encoder and zero the encoder.
#  @subsection testing Testing
#  The encoder driver was tested by running the code through an infinite while loop that continuously returned the value of the encoder. The encoder was manually turned by hand and the values were displayed in the command window. The encoder was turned as quickly as possible by hand and the encoder values increased in the correct direction. The driver was tested to +/-150,000, and the encoder count did not overflow or change values unexpectedly.
#  @subsection bugs Bugs_&_Limitations
#  There are no known bugs in the driver after the current testing. Because of the 16 bit counter, there is a frequency limit on the driver. For a motor rotating at 4000 RPM and an encoder with 4000 counts/revolution, the encoder must be read at a minimum of 8.138 Hz in order to ensure the delta between encoder readings does not overflow and cause inaccuracies. 
#  @bug read_encoder didn't reset timer counter. Resolved 1/24
#  @subsection location Location_of_Source_Code
#  http://wind.calpoly.edu/hg/mecha10