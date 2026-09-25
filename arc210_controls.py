"""Optional A-10C II ARC-210 bench controls using the documented address layout.

These simulate DCS-BIOS output to hardware, not commands to a running DCS.
"""
import math
import tkinter as tk
from tkinter import StringVar, OptionMenu, LEFT, E, W


class Arc210Controls:
    def buildArc210Controls(self):
        # ARC-210 direct bench-test controls.
        self.arc210ButtonF = tk.LabelFrame(self.topF, text="ARC-210")
        self.arc210ButtonF.pack(side=LEFT, padx=4)

        self.arc210MenuB = tk.Button(
            self.arc210ButtonF, text="MENU", width=9,
            command=lambda: self.sendArc210Momentary(
                "ARC210_MENU", 0x1334, 0x1000
            )
        )
        self.arc210MenuB.grid(row=0, column=0)

        self.arc210XmtRcvB = tk.Button(
            self.arc210ButtonF, text="XMT/RCV", width=9,
            command=lambda: self.sendArc210Momentary(
                "ARC210_TRANS_REC_FUNC", 0x1334, 0x0400
            )
        )
        self.arc210XmtRcvB.grid(row=0, column=1)

        self.arc210UpperLskB = tk.Button(
            self.arc210ButtonF, text="ULLSK", width=9,
            command=lambda: self.sendArc210Momentary(
                "ARC210_FSK_UP", 0x1366, 0x0400
            )
        )
        self.arc210UpperLskB.grid(row=1, column=0)

        self.arc210MiddleLskB = tk.Button(
            self.arc210ButtonF, text="MLLSK", width=9,
            command=lambda: self.sendArc210Momentary(
                "ARC210_FSK_MID", 0x1366, 0x0800
            )
        )
        self.arc210MiddleLskB.grid(row=1, column=1)

        self.arc210LowerLskB = tk.Button(
            self.arc210ButtonF, text="LLLSK", width=9,
            command=lambda: self.sendArc210Momentary(
                "ARC210_FSK_LOW", 0x1366, 0x1000
            )
        )
        self.arc210LowerLskB.grid(row=1, column=2)

        self.arc210FreqLabel = tk.Label(self.arc210ButtonF, text="Freq")
        self.arc210FreqLabel.grid(row=2, column=0, sticky=E)

        self.arc210Frequency = StringVar()
        self.arc210Frequency.set("133.000")
        self.arc210FrequencyE = tk.Entry(
            self.arc210ButtonF,
            width=8,
            textvariable=self.arc210Frequency
        )
        self.arc210FrequencyE.grid(row=2, column=1, sticky=W)

        self.arc210Modes = [
            "ECCM MASTER",
            "ECCM",
            "PRST",
            "MAN",
            "MAR",
            "243 GUARD",
            "121.500 GUARD"
        ]
        self.arc210Mode = StringVar()
        self.arc210Mode.set("MAN")
        self.arc210ModeMenu = OptionMenu(
            self.arc210ButtonF,
            self.arc210Mode,
            *self.arc210Modes
        )
        self.arc210ModeMenu.config(width=13)
        self.arc210ModeMenu.grid(row=3, column=1, columnspan=2)

        self.arc210SetFreqB = tk.Button(
            self.arc210ButtonF,
            text="Set FREQ",
            width=12,
            command=self.sendArc210Frequency
        )
        self.arc210SetFreqB.grid(row=2, column=2)

        self.arc210SecLabel = tk.Label(self.arc210ButtonF, text="Secondary")
        self.arc210SecLabel.grid(row=3, column=0, sticky=E)

        self.arc210SetSecondaryB = tk.Button(
            self.arc210ButtonF,
            text="Set Secondary",
            width=12,
            command=self.sendArc210Secondary
        )
        self.arc210SetSecondaryB.grid(row=3, column=3)

        # ARC210_MASTER values from the DCS-BIOS A-10C II definition.
        self.arc210MasterModes = [
            "0 - OFF",
            "1 - TR-G",
            "2 - TR",
            "3 - ADF",
            "4 - CHG PRST",
            "5 - TEST",
            "6 - ZERO"
        ]
        self.arc210MasterMode = StringVar()
        self.arc210MasterMode.set("2 - TR")

        self.arc210MasterLabel = tk.Label(self.arc210ButtonF, text="Master")
        self.arc210MasterLabel.grid(row=4, column=0, sticky=E)

        self.arc210MasterMenu = OptionMenu(
            self.arc210ButtonF,
            self.arc210MasterMode,
            *self.arc210MasterModes
        )
        self.arc210MasterMenu.config(width=13)
        self.arc210MasterMenu.grid(row=4, column=1, columnspan=2)

        self.arc210SetMasterB = tk.Button(
            self.arc210ButtonF,
            text="Set Master",
            width=12,
            command=self.sendArc210Master
        )
        self.arc210SetMasterB.grid(row=4, column=3)


    def _sendDirectWord(self, address, word, label):
        if not self.connectionIsOpen:
            print("Serial connection is not open")
            self.statusBar.set("%s", "Connect to the Teensy first")
            return False

        word &= 0xFFFF
        packet = (
            b"UUUU"
            + int(address).to_bytes(2, byteorder="little")
            + b"\x02\x00"
            + int(word).to_bytes(2, byteorder="little")
            + b"\xFE\xFF\x02\x00\x00\x00"
        )

        print("DIRECT ARC-210 BUTTON SEND")
        print("Name:", label)
        print("Address:", hex(address))
        print("Word:", hex(word))
        print("Packet:", packet)

        try:
            self.ser.write(packet)
            self.ser.flush()
        except OSError as error:
            self.statusBar.set("%s", "Serial write failed: " + str(error))
            return False
        self.dcsBiosValues[address] = word
        return True

    def sendArc210Momentary(self, name, address, mask):
        # Preserve every other control sharing the 16-bit DCS-BIOS word.
        current_word = int(self.dcsBiosValues.get(address, 0)) & 0xFFFF
        pressed_word = current_word | mask

        if not self._sendDirectWord(address, pressed_word, name + " PRESS"):
            return

        self.statusBar.set("%s", name + " pressed")

        connection = self.ser

        def release_button():
            if not self.connectionIsOpen or self.ser is not connection:
                return
            release_base = int(
                self.dcsBiosValues.get(address, pressed_word)
            ) & 0xFFFF
            released_word = release_base & ((~mask) & 0xFFFF)
            if self._sendDirectWord(
                address, released_word, name + " RELEASE"
            ):
                self.statusBar.set("%s", name + " released")

        self.topF.after(75, release_button)

    def _sendDirectString(self, address, value, max_length, label):
        if not self.connectionIsOpen:
            print("Serial connection is not open")
            self.statusBar.set("%s", "Connect to the Teensy first")
            return False

        data = value[:max_length].encode("ascii")
        data = data.ljust(max_length, b" ")
        data += b"\x00"
        if len(data) % 2:
            data += b"\x00"

        packet = (
            b"UUUU"
            + int(address).to_bytes(2, byteorder="little")
            + len(data).to_bytes(2, byteorder="little")
            + data
            + b"\xFE\xFF\x02\x00\x00\x00"
        )

        print("DIRECT ARC-210 STRING SEND")
        print("Name:", label)
        print("Address:", hex(address))
        print("Data:", data)
        print("Packet:", packet)

        try:
            self.ser.write(packet)
            self.ser.flush()
        except OSError as error:
            self.statusBar.set("%s", "Serial write failed: " + str(error))
            return False
        return True

    def sendArc210Frequency(self):
        try:
            frequency_value = float(self.arc210Frequency.get().strip())
        except ValueError:
            self.statusBar.set("%s", "Enter a frequency such as 133.000")
            return

        if not math.isfinite(frequency_value) or frequency_value < 30.0 or frequency_value > 399.975:
            self.statusBar.set("%s", "Frequency must be 30.000 to 399.975")
            return

        frequency_text = format(frequency_value, ".3f")
        if self._sendDirectString(
            0x1382, frequency_text, 7, "ARC210_FREQUENCY"
        ):
            self.statusBar.set("%s", "ARC-210 frequency " + frequency_text)

    def sendArc210Secondary(self):
        mode_value = self.arc210Modes.index(self.arc210Mode.get())
        current_word = int(self.dcsBiosValues.get(0x1322, 0)) & 0xFFFF
        current_word &= (~0xE000) & 0xFFFF
        current_word |= (mode_value << 13) & 0xE000

        if self._sendDirectWord(
            0x1322, current_word, "ARC210_SEC_SW " + self.arc210Mode.get()
        ):
            self.statusBar.set(
                "%s", "ARC-210 secondary " + self.arc210Mode.get()
            )

    def sendArc210Master(self):
        master_value = self.arc210MasterModes.index(
            self.arc210MasterMode.get()
        )
        current_word = int(self.dcsBiosValues.get(0x1322, 0)) & 0xFFFF
        current_word &= (~0x1C00) & 0xFFFF
        current_word |= (master_value << 10) & 0x1C00

        if self._sendDirectWord(
            0x1322,
            current_word,
            "ARC210_MASTER " + self.arc210MasterMode.get()
        ):
            self.statusBar.set(
                "%s", "ARC-210 master " + self.arc210MasterMode.get()
            )
