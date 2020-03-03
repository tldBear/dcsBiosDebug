#
#	DCS Bios Debug Tool
#
#
#
#
#	(c)2020 DRoberts


APP_VERSION = "V1.30 3/3/20"
APP_NAME = "BearTech dcsBiosDebug"

from os.path import expanduser
userHome = expanduser("~")

from tkinter import *
import tkinter as tk 
from tkinter import filedialog
import numpy as np
import sys
import os
import glob
import time
#find serial ports
import serial
import json
import re
from PIL import Image, ImageTk

print(sys.version)

class StatusBar :

    def __init__(self, master):
        #self.tk.Label = tk.Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.Label = tk.Label(master, anchor=W)
        self.Label.pack(side=BOTTOM, fill=X)


    def set(self, format, *args):
        self.Label.config(text=format % args)
        self.Label.update_idletasks()

    def clear(self):
        self.Label.config(text="")
        self.Label.update_idletasks()

class StringDisplay:

	def __init__(self, frame, name, address, mask):

		self.f = tk.LabelFrame(frame, text=name)
		self.f.grid( row = 1 + int( mWindow.widgetCount/2), column = int(mWindow.widgetCount % 2) )

		self.myText = StringVar()
		self.currentText = ""
		self.e = tk.Entry(self.f , width=20, textvariable=self.myText)
		self.e.pack(side=LEFT) 

		self.b = tk.Button(self.f, text='>', command=self.ButtonPress, width=1)
		self.b.pack(side=LEFT) 

		self.address = address
		self.max_length = mask
		self.count = 0
		self.changed = 0

	def __del__(self):
		print("Destroying")
		self.f.destroy()

	def ButtonPress(self) :
		print("String Element ")
		v = self.myText.get() + "                  "
		self.currentText = v.encode()
		#self.currentText = self.currentText[0:self.max_length]
		print(self.currentText)
		self.changed = 1
		self.count = 0
		self.updateAddr = self.address

	def getPacket(self) :
		packet = ""
		if self.changed :
			toSend = (self.address + self.max_length) - self.updateAddr
			if toSend > 4 :
				toSend = 4;
			if toSend > 1:
				v = self.currentText[self.count:self.count + toSend]
				l = b"" + np.uint8(toSend%256) + np.uint8(toSend/256)
				packet =  b"" + np.uint8(self.updateAddr%256) + np.uint8(self.updateAddr/256) + l + v
				self.count = self.count + toSend
				self.updateAddr = self.updateAddr + toSend
				if self.updateAddr >= self.address + self.max_length :
					self.changed = 0
				print(packet)
		return packet


class LEDButton:


	def __init__(self, frame, name, address, mask):

		self.ButtonB = tk.Button(frame, text=name, command=self.ButtonPress, highlightbackground="white", width=20)
		self.ButtonB.grid( row = 1 + int( mWindow.widgetCount/2), column = int(mWindow.widgetCount % 2) )

		self.address = address
		self.mask = mask
		self.imask = np.invert(mask)
		self.state = 0
		self.changed = 0

	def __del__(self):
		print("Destroying")
		self.ButtonB.destroy()

	def ButtonPress(self) :
		print("LED Button")
		if self.state :
			self.state = 0
			self.ButtonB.configure(highlightbackground="white")
			self.ButtonB.configure(background="white")
			self.changed = 1
		else :
			self.state = 1
			self.ButtonB.configure(highlightbackground="green")
			self.ButtonB.configure(background="green")
			self.changed = 1

	def getPacket(self) :
		packet = ""
		if self.changed :
			if self.state :
				v = b"" + np.uint8(self.mask % 256) + np.uint8(self.mask / 256)
			else :
				v = b"\x00\x00"
			packet =  b"" + np.uint8(self.address%256) + np.uint8(self.address/256) + b"\x02\x00" + v
			self.changed = 0
		return packet


###### End LEDtk.Button

class IntSlider:

	def __init__(self, frame, name, address):

		
		self.address = address
		self.value = StringVar()
		self.changed = 0

		self.f = tk.LabelFrame(frame, text=name, width=30)
		self.f.grid( row = 1 + int( mWindow.widgetCount/2), column = int(mWindow.widgetCount % 2) )

		self.autoUpdate = IntVar()
		self.cb = tk.Checkbutton(self.f, variable=self.autoUpdate, text="Auto")
		self.cb.grid(row=1, column=0)

		self.autoRate = StringVar()

		self.l = tk.Entry(self.f, textvariable=self.autoRate, width=3)
		self.l.grid(row=1, column=1)

		self.ll = tk.Label(self.f, text="/s")
		self.ll.grid(row=1, column=3)

		self.autoWrap = IntVar()
		self.cb = tk.Checkbutton(self.f, variable=self.autoWrap, text="Wrap")
		self.cb.grid(row=1, column=4)

		self.intS = tk.Scale(self.f, command=self.sliderMove, from_ = 0, to = 65535, orient=HORIZONTAL, variable=self.value, width=10, length=200)
		self.intS.grid(row=0, column=0, columnspan=5, sticky=W+E)

		self.autoValue = np.int32(0)	#so can handle overflow	
		self.nextUpdate = time.monotonic()
		self.dir = 1
		self.autoCount = 2

	def __del__(self):
		print("Destroying")
		self.f.destroy()

	def sliderMove(self, value) :
		print(self)
		print("Int Slider" + value + " " + str(self.address))
		self.value = np.uint16(value)
		self.changed = 1

	def getPacket(self) :
		packet = ""
		if self.autoUpdate.get() :
			if time.monotonic() > self.nextUpdate :
				print(self.value)
				#a = np.uint16(self.value)*np.uint16(self.dir)
				self.autoValue = self.autoValue + self.value* self.dir
				
				#check for wrapping condition
				if self.autoWrap.get() :
					if self.autoValue > 65535 :
						if self.autoCount == 0:
							self.autoValue = 65535
							self.autoCount = 2
							self.dir = self.dir * -1
						else :
							self.autoValue = self.autoValue - 65536
							self.autoCount=self.autoCount-1

					if self.autoValue < 0 :
						if self.autoCount == 0:
							self.autoValue = 0
							self.autoCount = 2
							self.dir = self.dir * -1
						else :
							self.autoValue = self.autoValue + 65536
							self.autoCount=self.autoCount-1

					
				else :
					if self.autoValue > 65535 :
						self.autoValue = 65535
						self.dir = self.dir * -1

					if self.autoValue < 0 :
						self.autoValue =  0
						self.dir = self.dir * -1

				tempAutoValue = np.uint16(self.autoValue)
				print(self.autoValue)
				print(tempAutoValue)
				#get update interval
				tt = self.autoRate.get()
				
				try:
					noUpdates = float(tt)
				except:
					noUpdates = 1
					#print("Non-Number Argument")
				if noUpdates > 0 and noUpdates < 31:
					interval = 1/noUpdates
				else :
					interval = 1

				self.nextUpdate = time.monotonic() + interval
				packet =  b"" + np.uint8(self.address%256) + np.uint8(self.address/256) + b"\x02\x00" + np.uint8(tempAutoValue % 256) + np.uint8(tempAutoValue / 256)
				#print(packet)
		else :
			self.autoValue = self.value
			if self.changed :
				packet =  b"" + np.uint8(self.address%256) + np.uint8(self.address/256) + b"\x02\x00" + np.uint8(self.value % 256) + np.uint8(self.value / 256)
				self.changed = 0
		return packet

###### End IntSlider

class catCreator:

	def __init__(self, listFrame, name):

		self.name = name


		self.ButtonB = tk.Button(listFrame, text=name, command=self.ButtonPress, highlightbackground="white", width=30)
		self.ButtonB.pack(anchor=W)

		self.ff = tk.Frame(listFrame, width = 40, height = 4)
		self.ff.pack()

		self.showF = 1

	def ButtonPress(self):
		if self.showF :
			self.showF = 0
			self.ff.config(height = 0)
		else :
			self.showF = 1
			self.ff.config(height = 10)

#######################################

class widgetCreator:

	def __init__(self, listFrame, widgetFrame, type, name, address, mask, imageToUse ):
		self.widgetFrame = widgetFrame
		self.type = type
		self.name = name
		self.address = address
		self.mask = mask
		self.imageToUse = imageToUse
		self.ll = tk.Label(listFrame)
		self.ll.pack()
		self.img = tk.Label(self.ll, image=self.imageToUse)
		self.img.image = self.imageToUse
		#self.img.place(x=0, y=0)
		self.img.pack(side=LEFT)
		self.ButtonB = tk.Button(self.ll, text=name, command=self.ButtonPress, highlightbackground="white", width=36)
		self.ButtonB.pack(side=LEFT)


		mWindow.instrumentList['Active'][self.name] = self

	def ButtonPress(self):
		if self.type == 'led':
			mWindow.dcsBiosButtons.append( LEDButton(self.widgetFrame, self.name, np.uint16(self.address), np.uint16(self.mask)))
			mWindow.dcsBiosAddressOrder[self.address] = mWindow.widgetCount
			mWindow.widgetCount = mWindow.widgetCount + 1


		if self.type == 'analog_gauge':
			mWindow.dcsBiosButtons.append( IntSlider(self.widgetFrame, self.name, np.uint16(self.address)))
			mWindow.dcsBiosAddressOrder[self.address] = mWindow.widgetCount
			mWindow.widgetCount = mWindow.widgetCount + 1

		if self.type == 'display':
			mWindow.dcsBiosButtons.append( StringDisplay(self.widgetFrame, self.name, np.uint16(self.address), self.mask))
			mWindow.dcsBiosAddressOrder[self.address] = mWindow.widgetCount
			mWindow.widgetCount = mWindow.widgetCount + 1

		
		mWindow.appSettings['Active'][self.name] = self.type


#######################################

class DCSDebugWindow:
	
	connectionIsOpen = 0 
	serPorts = []
	ser = serial.Serial()
	tickCounter = 0
	nextUpdate = time.monotonic()
	updateCount = np.uint16(0)
	dcsBiosButtons = []
	dcsBiosAddressOrder = {}
	widgetCount = 0

	appSettings = {}
	appSettings['Active'] = {}
	instrumentList = {}
	instrumentList['Active'] = {}

	#Create Main Window title="Bear DCSBios Debug Tool"
	def __init__(self, master ):


		master.geometry("1088x712")
		master.title(APP_NAME + " " + APP_VERSION)



		#controls
		self.topF = tk.Frame(master, relief="raised")
		self.topF.pack( anchor = W, fill=X)

		self.mainF = tk.Frame(master)
		self.mainF.pack( anchor = W)
		
		self.statusBar = StatusBar(master)
		self.statusBar.set("%s", "Ready")

		

		


		#Recv Data 
		self.rightF = tk.LabelFrame(self.mainF, height = 30, text="Recv Text", width=50)
		self.rightF.grid(row=0, column=0, rowspan=20)

		#Recv Data
		
		self.recvTextVariable = StringVar()
		self.recvText = tk.Label(self.rightF, textvariable = self.recvTextVariable, height=40, width = 30,  anchor=NW, justify=LEFT)
		self.recvText.pack(anchor=N)
		#self.recvText.insert(END,"Hello")


		#Scrollable Frame
		fileF = tk.LabelFrame(self.mainF, width = 50, height=1, text="DCSBios File")
		fileF.grid(row=0, column=1, sticky="nsew")

		loc = tk.LabelFrame(self.mainF, width = 50, height=50,text="Categories")

		loc.grid(row=1, column=1, sticky="nsew", rowspan=19)

		canvas = Canvas(loc, width=360)
		scrollbar = Scrollbar(loc, orient="vertical", command=canvas.yview)
		self.scrollable_frame = Frame(canvas,width = 45)

		self.scrollable_frame.bind(
		    "<Configure>",
		    lambda e: canvas.configure(
		        scrollregion=canvas.bbox("all")
		    )
		)

		canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

		canvas.configure(yscrollcommand=scrollbar.set)


		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")
		
		self.fileNameVariable = StringVar()
		self.fileNameVariable.set("Choose DCSBios json File")
		self.fileName = tk.Label(fileF, textvariable = self.fileNameVariable, width=40, justify=LEFT)
		self.fileName.pack(side="left")

		self.chooseJSONFileB = tk.Button(fileF, text=">")
		self.chooseJSONFileB.bind("<Button-1>", self.chooseJSONFile)
		self.chooseJSONFileB.pack(side=RIGHT)

		#Scrollable Frame End

		#master.grid_columnconfigure(0,weight=1)
		#master.grid_columnconfigure(1,weight=1)
		#master.grid_rowconfigure(0,weight=1)
		#master.grid_rowconfigure(1,weight=1)

		#Action tk.Buttons
		self.btmF = tk.LabelFrame(self.mainF, text="Active Instruments", width = 50)
		self.btmF.grid(row=0, column=2, rowspan=20, sticky=NW)

		#Controls


		self.findSerPortsB = tk.Button(self.topF, text="Find Serial Ports")
		self.findSerPortsB.bind("<Button-1>", self.findSerPorts)
		self.findSerPortsB.pack(side=LEFT)

		self.serialPortList =  serial_ports() 
		if len(self.serialPortList) == 0 :
			self.serialPortList = ["-"]
		#self.serialPortList = ["aa", "bb", "cc"]
		print(self.serialPortList)

		self.serialPortChoice = StringVar()
		self.serialPortChoice.set("-")
		self.listB = OptionMenu(self.topF, self.serialPortChoice, *self.serialPortList)
		self.listB.pack(side=LEFT)

		

		

		self.connectButtonText = StringVar()
		self.connectButtonText.set("Connect")
		self.connectB = tk.Button(self.topF, textvariable=self.connectButtonText)
		self.connectB.bind("<Button-1>", self.toggleConnection)
		self.connectB.pack(side=LEFT)
		
		self.intervalF = Frame(self.topF)
		self.intervalF.pack(side=LEFT)

		self.intervalL = tk.Label(self.intervalF, text="Updates")
		self.intervalL.grid(row=0, column=0)

		self.noUpdates = IntVar()
		self.intervalE = tk.Entry(self.intervalF, width=2, textvariable=self.noUpdates)
		self.intervalE.grid(row=0, column=1)

		self.intervalL = tk.Label(self.intervalF, text="/s")
		self.intervalL.grid(row=0, column=2)

		self.saveRecvData = 1
		self.saveRecvDataC = tk.Checkbutton(self.topF,text="Save Recv Data", variable=self.saveRecvData)
		self.saveRecvDataC.pack(side=LEFT)

		self.btmCFrame = tk.Frame(self.btmF, width = 50)
		self.btmCFrame.grid(row=0, column=0, columnspan=2, sticky=NW)

		self.clearB = tk.Button(self.btmCFrame, text="Clear", width=8)
		self.clearB.bind("<Button-1>", self.clear)
		self.clearB.pack(side=LEFT)

		self.loadB = tk.Button(self.btmCFrame, text="Load", width=8)
		self.loadB.bind("<Button-1>", self.loadUserSettings)
		self.loadB.pack(side=RIGHT, anchor=E)

		self.saveB = tk.Button(self.btmCFrame, text="Save", width=8)
		self.saveB.bind("<Button-1>", self.saveUserSettings)
		self.saveB.pack(side=RIGHT, anchor=E)

		self.quitAppB = tk.Button(self.topF, text="Quit", width=8)
		self.quitAppB.bind("<Button-1>", self.quitApp)
		self.quitAppB.pack(side=RIGHT, anchor=E)

		

	def loadUserSettings(self, event):
		print("Load")	
		openFile =  filedialog.askopenfilename(title = "Select file",filetypes = (("settings files","*.json"),("all files","*.*")))
		print(openFile)
		if openFile != "" :
			self.readSettingsFile(openFile) 

	def saveUserSettings(self, event):
		print("Save")
		files = [('All Files', '*.*'),  
             ('Settings Files', '*.json')] 
    

		openFile =  filedialog.asksaveasfilename( defaultextension = 'json')
		with open(openFile, 'w') as f :
			json.dump(self.appSettings, f)
			f.close()

	def readDefaultSettingsFile(self) :

		settingsFile = userHome + '/Documents/dcsBiosDebugSettings.json'

		self.readSettingsFile(settingsFile)

	def readSettingsFile(self, settingsFile) :
		#Read Config File
		settingsTemp = {}
		try:
			
			with open(settingsFile, 'r') as f :
				settingsTemp = json.load(f)
				f.close()
		except:
			print("Can't Open "+settingsFile)

		if "JSONFile" in settingsTemp:
			print(settingsTemp["JSONFile"])
			self.readJSONData( settingsTemp["JSONFile"])

			#print(mWindow.instrumentList)
			if "Active" in settingsTemp:
				for inst in settingsTemp['Active'].keys():
					print(inst)
					mWindow.instrumentList['Active'][inst].ButtonPress()

			if 'noUpdates' in settingsTemp:
				mWindow.noUpdates.set(settingsTemp['noUpdates'])

		#self.dcsBiostk.Buttons.append( LEDtk.Button(self.btmF, "Waypoints", np.uint16(0x1920), np.uint16(0x0400)))
		#self.dcsBiosAddressOrder[0x1920] = 0

		#self.dcsBiostk.Buttons.append( LEDtk.Button(self.btmF, "Wind Hdg/Spd", np.uint16(0x1932), np.uint16(0x0400)))
		#self.dcsBiosAddressOrder[0x1932] = 1

	#	self.dcsBiostk.Buttons.append( IntSlider(self.btmF, "Mag var 1", np.uint16(0x1942)))
		#self.dcsBiosAddressOrder[0x1942] = 2

	def chooseJSONFile(self, event) :
		print("Open File")
		openFile =  filedialog.askopenfilename(title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
		print(openFile)
		if openFile != "" :
			self.readJSONData( openFile)
			

	def findSerPorts(self,event) :
		print("Poll Serial")
		self.serialPortList =  serial_ports() 

		print(self.serialPortList)
		if len(self.serialPortList) == 0 :
			self.serialPortList = ["-"]
		self.serialPortChoice.set("-")
		self.listB['menu'].delete(0, 'end') 
		
		for choice in self.serialPortList :
			self.listB['menu'].add_command(label=choice, command=tk._setit(self.serialPortChoice, choice))

	def readJSONData(self, fileName) :
		self.fileNameVariable.set(fileName)
		self.appSettings["JSONFile"] =fileName

		file_path = resource_path("./icons/led.png")
		load = Image.open(file_path)
		self.ledI = ImageTk.PhotoImage(load)

		file_path = resource_path("./icons/text.png")
		load1 = Image.open(file_path)
		self.textI = ImageTk.PhotoImage(load1)

		file_path = resource_path("./icons/gauge.png")
		load2 = Image.open(file_path)
		self.gaugeI = ImageTk.PhotoImage(load2)

		#Read json file

		with open(fileName, 'r') as f :
			data = json.load(f)

			for cat in sorted(data) :
				catF = catCreator(self.scrollable_frame, cat)

				catData = data[cat]
				for con in sorted(catData) :
					conData = catData[con]

					controlType = conData['control_type']
					if controlType == 'display' :
						address = conData['outputs'][0]['address']
						max_length = conData['outputs'][0]['max_length']
						widgetCreator(catF.ff ,self.btmF, controlType, con, address, max_length, self.textI )

					if controlType == 'led' :
						address = conData['outputs'][0]['address']
						mask = conData['outputs'][0]['mask']
						widgetCreator(catF.ff ,self.btmF, controlType, con, address, mask, self.ledI )

					if controlType == 'analog_gauge' :
						address = conData['outputs'][0]['address']
						widgetCreator(catF.ff ,self.btmF, controlType, con, address, 0, self.gaugeI )

			f.close()

	def quitApp(self, event):
		#save current settings
		settingsFile = userHome + '/Documents/dcsBiosDebugSettings.json'
		with open(settingsFile, 'w') as f :
			json.dump(self.appSettings, f)
			f.close()
		root.quit()
	#	self.clear("<Button-1>")
	#	root.destroy()


	def clear(self, event):
		for wid in mWindow.dcsBiosButtons:
			wid.__del__()
		mWindow.widgetCount = 0
		mWindow.dcsBiosAddressOrder.clear()


	def toggleConnection(self,event):

		
		if self.connectionIsOpen :
			self.connectionIsOpen = 0
			print("Close Connection")
			self.connectButtonText.set("Connect")
			self.ser.close() 
			self.statusBar.set("%s", "Ready")
		else :
			
			print("Try to Open Connection on " + self.serialPortChoice.get() )
			
			if self.serialPortChoice.get() != "-" :
				try:
					self.ser = serial.Serial(self.serialPortChoice.get(), 250000, timeout=0, rtscts=0)  # open serial port
				except:
					self.ser = ""
				print(">" + str(self.ser) + "<")
				if self.ser == "" :
					print("Failed")
					print("No Serial Port Found/Accessible: Try another")

				else :
					print("Successful")
					self.connectionIsOpen = 1
					self.nextUpdate = time.monotonic() + 1.5
					self.connectButtonText.set("Close")
					self.runUp = 3
					self.statusBar.set("%s", "Connected to:" + self.serialPortChoice.get())
			else :
				print("Select a Serial Port")

	
	
#########################################end of class

def replayFile(ports):
	for port in ports:
		ser = serial.Serial(port, 250000, timeout=0, rtscts=0)  # open serial port

		print(ser.name)         # check which port was really used
		time.sleep(0.5)
		#ss = b'UUUU\x10\x00\x02\x00  \xfe\xff\x02\x00\x00\x00'

		

		time.sleep(0.05)
		s = ser.read(100)
		
		print(s)
		print('--------')

		
		with open('dcsBiosInit.dmp', 'rb') as f :
			print('Looking for Ident')

			data = 1
			while data != b'' :
				data = f.read(1)
				#ser.write(data)
				print(data)


			time.sleep(0.5)
			s = ser.read(100)
		
			print(s)
			print('--------')

			f.close()

	keepSending = 1

	while keepSending :
		time.sleep(5)

		mc = 0
		frame = 0
		#open file
		with open('dcsBios.dmp', 'rb') as f, open('dcsBiosRecv.dmp', 'wb') as frecv :
			print('FileStart')

			data = 1
			while data != b'' :
				data = f.read(1)
				#print(data)
				

				if data == b'U' :
				
					#read byte from file
					data2 = f.read(1)
					if data2 == b'U' :
					
						data3 = f.read(1)
						if data3 == b'U' :
						
							data4 = f.read(1)
							if data4 == b'U' :
								frame = 1
								#print("Frame")
							else :
								ser.write(data)
								ser.write(data2)
								ser.write(data3)
								ser.write(data4)

						else :
							ser.write(data)
							ser.write(data2)
							ser.write(data3)

					else :
						ser.write(data)
						ser.write(data2)

				else :
					frecv.write(data)
					ser.write(data)

				if data == b'\x14' :
					mc = 1

				if mc == 1 and data == b'\x18' :
					mc = 2
				else :
					mc = 0

				if mc == 2 and data == b'\x06' :
					mc = 3
				else :
					mc = 0

				if mc == 4 and data == b'\x00' :
					mc = 0
					print("MC")

				if frame == 1 :
					print("***********")
					#repeat 30 times a second
					time.sleep(0.033)
					s = ser.read(20)
					print(s)
					#write this to recv file
					frecv.write(b'****')
					frecv.write(s)
					frecv.write(b'****')
					frecv.write(b'UUUU')
					
					ser.write(b'UUUU')
					
					frame = 0



		#end loop


		f.close()
		frecv.close()


	ser.close() 

def serial_ports():
	""" Lists serial port names

		:raises EnvironmentError:
			On unsupported or unknown platforms
		:returns:
			A list of the serial ports available on the system
	"""
	if sys.platform.startswith('win'):
		ports = ['COM%s' % (i + 1) for i in range(256)]
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		# this excludes your current terminal "/dev/tty"
		ports = glob.glob('/dev/tty[A-Za-z]*')
	elif sys.platform.startswith('darwin'):
		ports = glob.glob('/dev/cu.usb*')
	else:
		raise EnvironmentError('Unsupported platform')

	result = []
	for port in ports:
		#print(port)
		try:
			s = serial.Serial(port)
			s.close()
			result.append(port)
		except (OSError, serial.SerialException):
			pass
	return result

####################################################
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



###############################################

def update() :
	
	try:
		noUpdates = mWindow.noUpdates.get()
	except:
		noUpdates = 1



	mWindow.noUpdates.set(noUpdates)

	if noUpdates > 0 and noUpdates < 31:
		interval = 1/noUpdates
	else :
		interval = 1/30

	mWindow.appSettings['noUpdates'] = noUpdates

	#print(interval)

	if mWindow.connectionIsOpen :
		if time.monotonic() > mWindow.nextUpdate :
			print("Update")
			mWindow.nextUpdate = time.monotonic() + interval
			###############################################
			packet = b'UUUU' 

			if mWindow.runUp :
				mWindow.runUp = mWindow.runUp - 1
			else :
				for c in sorted(mWindow.dcsBiosAddressOrder) :


					packet1 = mWindow.dcsBiosButtons[mWindow.dcsBiosAddressOrder[c]].getPacket()
					if len(packet1) > 0 :
						#mWindow.ser.write(packet)
						packet = packet + packet1
				
				#send end of update
				#packet = packet + b"\xFE\xFF\x02\x00" + np.uint8(mWindow.updateCount%256) + np.uint8(mWindow.updateCount/256)
				packet = packet + b"\xFE\xFF\x02\x00" + np.uint8(mWindow.updateCount%256) + b"\x00"


			print(packet)
			mWindow.ser.write(packet)

			q = mWindow.recvTextVariable.get() 
			s = ""
			for sTemp in q.splitlines()[-39:60] :
				s = s + sTemp + "\n"

			packet = mWindow.ser.read(30)
			s = s + str(packet) + "\n"

			mWindow.recvTextVariable.set(s)



	mWindow.updateCount = mWindow.updateCount + 1
	#print(mWindow.updateCount)
	root.after(10, update)


####################################################


#if __name__ == '__main__':
#serPorts =  serial_ports() 
#print(serPorts)
#replayFile(serPorts)

root = tk.Tk()
mWindow = DCSDebugWindow(root) 
mWindow.readDefaultSettingsFile()
#mWindow.readJSONData()

update()

root.mainloop()

print("Exiting")
#save config

#quit()

