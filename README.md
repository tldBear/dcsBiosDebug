 # dcsBiosDebug  ![App Icon](iconDebugSmall.png)
 
App to help debug DCSBios instruments.

Note
This is still a work in progress. Bugs are expected.

![App Screenshot](manual/appScreenshot.png)

# Concept

Often when building/debugging dcsBios based instruments, it can be useful to be able to send to the instrument a particular update message, gauge value etc without having start DCS, start a mission, try to fly whilst debugging etc
This app is designed to just that. It's a small GUI that allows you to send instrument state updates over a serial port to your cockpit hardware and view their responses.

# Updates
**1.4.0**

Various bug fixes. Added 'Calibration' widget. Can send text to listening instrument, give it commands to set calibration point.

**v1.3.4**

Improved recv text

**v1.3.3**

Fixed single byte text field

**v1.3.2**

Fixed LED behaviour

**v1.3** 

Added Save/Load User settings

Saves settings on close

Added checking of fields

Testing of IntegerBuffer

Misc bugs fixed

# Downloads

v1.4

### Pre Built Binaries

[**Windows 64bit**](https://github.com/tldBear/dcsBiosDebug/releases/download/v1.4.0/Win64_1.4.0_dcsBiosDebug.exe)

Should be fully self contained. 
 
### Python script

[**Mac OSX App Bundle**](https://github.com/tldBear/dcsBiosDebug/releases/download/v1.4.0/MacOSX_1.4.0_dcsBiosDebug.app.zip)


[**Source**](https://github.com/tldBear/dcsBiosDebug/releases/tag/v1.4.0)

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
(max 30/s)


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

Integer Fields can also send updates automatically. Click the 'Auto' button.
![IntAuto](manual/ScreenshotInt1.png)

Integer Field will then increment at set rate slider value, '/s' times per second,  until 65535 reached, then start decrementing until zero. Then repeat.
If 'Wrap' is set, in Auto mode will wrap from 65535 to zero and continue incrementing until reaching 65535 the second time. Then will start decrementing, again wrapping from 0 to 65535. At end of second cycle will repeat.

![IntAutoWrap](manual/ScreenshotInt2.png)

In the above example, the Integer will start from 0, increment to 2, then 4 ect, 12 times per second. On reaching 65535, it'll reset to 0, and then continue to 65535 a second time. it'll then start decrementing, reset to 65535 when it reaches 0, and continue until it reaches 0 again. It'll then start incrementing again.



# Limitations and known bugs

Save Received Data not implemented.

Integer Fields only 16bit.



# Further Work
Remove above limitations :-)

Add ability to remove individual indicators.


**Suggestions for improvement and bug reports are welcome**



## Optional ARC-210 bench controls

Start the Python app with `python dcsBiosDebug.py --arc210` to show an additional
A-10C II ARC-210 panel beside the serial controls. Without this flag, the normal
interface is unchanged. Connect to your hardware using the existing serial controls.

The panel provides MENU, XMT/RCV, upper/middle/lower left soft keys, and separate
Set Frequency, Set Secondary, and Set Master controls. Master includes OFF and TR.
Frequency accepts 30.000–399.975 MHz. Each momentary button sends a press followed
by a release after 75 ms. Changing Master preserves Secondary and the other fields
sharing its word; changing Secondary preserves Master. Setting frequency does not
turn on the radio or change either switch.

These controls send simulated DCS-BIOS output packets directly to the connected
hardware. They do not operate the radio in a running DCS session. They use a fixed
A-10C II export layout, independently of the JSON selected in the main app:

| Control | Address | Mask / length |
| --- | --- | --- |
| Master | 0x1322 | 0x1C00, shift 10 |
| Secondary | 0x1322 | 0xE000, shift 13 |
| Frequency | 0x1382 | 7 characters |
| MENU / XMT/RCV | 0x1334 | 0x1000 / 0x0400 |
| Upper / middle / lower soft key | 0x1366 | 0x0400 / 0x0800 / 0x1000 |

Check these against your installed DCS-BIOS aircraft JSON before use. Do not enable
this panel for another aircraft or address layout. Existing automatic updates for
the same controls can overwrite bench settings; disable those while testing.
Firmware that requires additional power/status exports may need those supplied
through the normal controls as well. No new dependencies are required.

Protocol tests can be run with `python -m unittest discover -s tests`.
