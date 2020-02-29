 # dcsBiosDebug  ![App Icon](iconDebugSmall.png)
 
App to help debug DCSBios instruments.

Note
This is still a work in progress. Bugs are expected.

![App Screenshot](manual/appScreenshot.png)

# Concept

Often when building/debugging dcsBios based instruments, it can be useful to be able to send to the instrument a particular update message, gauge value etc without having start DCS, start a mission, try to fly whilst debugging etc
This app is designed to just that. It's a small GUI that allows you to send instrument state updates over a serial port to your cockpit hardware and view their responses.

# Downloads

### Pre Built Binaries

[Windows 64bit](https://github.com/tldBear/tldBear.github.io/blob/master/Downloads/dcsBiosDebug.exe)

Should be fully self contained. 
 
### Python script

[**Mac OSX App Bundle**](https://github.com/tldBear/tldBear.github.io/blob/master/Downloads/dcsBiosDebug.zip)




[**GitHub Project**](https://github.com/tldBear/dcsBiosDebug)

**Note** These are not fully self contained. Python3, as well as some dependancies (eg tkinter, pyserial & numpy) will need to be installed separately.


# Usage

## Select and Connect Serial Port
Click 'Find Serial Ports', then choose from drop down list the serial port your Arduino is connected to.

![Find Serial Ports](manual/Screenshot_Serial0.png)

![Choose Serial Port](manual/ScreenshotSerial1.png)

Next click 'Connect'

![Choose Serial Port](manual/Screenshot_SerialConnect.png)

Serial Port should then open. dcsBiosDebug will start sending updates to connected Arduinos, and print any responses to the Recv Text window.

![Choose Serial Port](manual/Screenshot_SerialOpen.png)

By default, dcsBiosDebug will send one update per second. This can be increased by setting the value in the update/s field.
(max 30)
**Note** There's currently no error checking on this field. Entering something other than an integer value will cause an error in the app. You'll need to restart.

## Choose JSON File
Next, need to choose DCS Bios JSON file that defines instruments, buttons etc. These should be in the doc/json directory of DCS Bios. 

Click '>', browse to JSON file for your aircraft in DCS Bios folder and click 'Open'.
![Choose JSON](manual/ScreenshotJSON.png)

Categories area should get populated with all the various gauges, LEDs etc defined for your aircraft.
![JSON Loaded](manual/ScreenshotJSONLoaded.png)

## Make the required controls active
Now need to make active the controls you want debug in this session.

Scroll down to the particular instrument, and click on the entry for the LED, gauge or text field to debug. This will add it to the Active Indicator area. 
![LED](manual/ScreenshotLED.png)

Eg In this screen shot, controls for the Ka50 PVI-800 are being debugged. The PVI_WAYPOINTS_LED has been added.

Add other indicators as required. Clicking 'Clear' will remove all indicators.

Clicking on the LED will toggle its state.



**Text Fields**, click in Categories to add to Active Indicators. Enter the text to send, then click the '>' button to send the update.

![Text](manual/ScreenshotText2.png)

**Integer Fields**
Again, click to make active. Drag slider to send update value to instrument.

![Int](manual/ScreenshotInt.png)

Int Fields can also send updates automatically. Click the 'Auto' button.
![IntAuto](manual/ScreenshotInt1.png)

Integer Field will then increment at set rate slider value, '/s' times per second,  until 65535 reached, then start decrementing until zero. Then repeat.
If 'Wrap' is set, in Auto mode will wrap from 65535 to zero and continue incrementing until reaching 65535 the second time. Then will start decrementing, again wrapping from 0 to 65535. At end of second cycle will repeat.

![IntAutoWrap](manual/ScreenshotInt2.png)

In the above example, the Integer will start from 0, increement to 2, then 4 ect, 12 times per second. On reaching 65535, it'll reset to 0, and then continue to 65535 a second time. it'll then start decrementing, reset to 65535 when it reaches 0, and continue until it reaches 0 again. It'll then start incrementing again.

**Note** Integer Field hasn't been fully verified. Regard this part of App as alpha quality.

# Limitations and known bugs
Field entry value checking as noted above.

Integer Field not fully verified.

Save Received Data not implemented.

Integer Fields only 16bit.

Quit button doesn't work on Windows. Hit x or kill app.


# Further Work
Remove above limitations :-)

Save Active Indicator to a file.

Add ability to remove individual indicators.


**Suggestions for improvement and bug reports are welcome**

