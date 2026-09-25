import unittest
from types import SimpleNamespace
from arc210_controls import Arc210Controls


class Port:
    def __init__(self):
        self.packets = []

    def write(self, packet):
        self.packets.append(packet)

    def flush(self):
        pass


class Bench(Arc210Controls):
    def __init__(self):
        self.ser = Port()
        self.connectionIsOpen = True
        self.dcsBiosValues = {}
        self.statusBar = SimpleNamespace(set=lambda *args: None)
        self.callbacks = []
        self.topF = SimpleNamespace(after=lambda ms, cb: self.callbacks.append(cb))
        self.arc210Modes = ['ECCM MASTER', 'ECCM', 'PRST', 'MAN', 'MAR', '243 GUARD', '121.500 GUARD']
        self.arc210MasterModes = list(range(7))


class ControlsTest(unittest.TestCase):
    def test_master_and_secondary_preserve_shared_fields(self):
        b = Bench()
        for seed in (0, 0xFFFF, 0xA555):
            for value in range(7):
                b.dcsBiosValues[0x1322] = seed
                b.arc210MasterMode = SimpleNamespace(get=lambda: value)
                # Labels in the real UI are strings; use them here too.
                b.arc210MasterModes = [str(i) for i in range(7)]
                b.arc210MasterMode.get = lambda: str(value)
                b.sendArc210Master()
                self.assertEqual(b.dcsBiosValues[0x1322], (seed & ~0x1C00) | (value << 10))
                b.dcsBiosValues[0x1322] = seed
                b.arc210Mode = SimpleNamespace(get=lambda: b.arc210Modes[value])
                b.sendArc210Secondary()
                self.assertEqual(b.dcsBiosValues[0x1322], (seed & ~0xE000) | (value << 13))

    def test_press_release_keeps_intervening_changes(self):
        b = Bench()
        b.dcsBiosValues[0x1334] = 2
        b.sendArc210Momentary('MENU', 0x1334, 0x1000)
        self.assertEqual(b.ser.packets[0], b'UUUU\x34\x13\x02\x00\x02\x10\xfe\xff\x02\x00\x00\x00')
        b.dcsBiosValues[0x1334] |= 4
        b.callbacks.pop()()
        self.assertEqual(b.dcsBiosValues[0x1334], 6)

    def test_release_does_not_cross_connections(self):
        b = Bench()
        b.sendArc210Momentary('MENU', 0x1334, 0x1000)
        b.ser = Port()
        b.callbacks.pop()()
        self.assertEqual(b.ser.packets, [])

    def test_frequency_packet_and_validation(self):
        b = Bench()
        for value in ('nan', 'inf', 'bad', '29.999', '400'):
            b.arc210Frequency = SimpleNamespace(get=lambda: value)
            b.sendArc210Frequency()
        self.assertEqual(b.ser.packets, [])
        b.arc210Frequency = SimpleNamespace(get=lambda: '133.000')
        b.sendArc210Frequency()
        self.assertEqual(b.ser.packets, [b'UUUU\x82\x13\x08\x00133.000\x00\xfe\xff\x02\x00\x00\x00'])
        self.assertEqual(b.dcsBiosValues, {})

    def test_disconnected_and_failed_writes(self):
        b = Bench()
        b.connectionIsOpen = False
        self.assertFalse(b._sendDirectWord(0x1322, 2, 'test'))
        self.assertEqual(b.ser.packets, [])
        b.connectionIsOpen = True
        def fail(packet):
            raise OSError('disconnected')
        b.ser.write = fail
        self.assertFalse(b._sendDirectWord(0x1322, 2, 'test'))
        self.assertEqual(b.dcsBiosValues, {})


if __name__ == '__main__':
    unittest.main()
