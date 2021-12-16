
# coding: utf-8
 
import sys
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import *
 
import statistics
import obd
from obd import OBDCommand, Unit
from obd.utils import bytes_to_int


class PiHud(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.ui = loadUi("resources/pi-hud.ui")
        self.obdWorker = OBDWorker()
        self.connectSignalSlot()
        self.obdWorker.start()
        self.speedFilter = [0, 0, 0, 0, 0, 0]

    def connectSignalSlot(self):
        self.obdWorker.rpmSignal.connect(self.rpmUpdateSlot)
        self.obdWorker.speedSignal.connect(self.speedUpdateSlot)
        self.obdWorker.tempSignal.connect(self.tempUpdateSlot)
        self.obdWorker.loadSignal.connect(self.loadUpdateSlot)
        self.obdWorker.dpfDistSignal.connect(self.dpfDistUpdateSlot)
        self.obdWorker.dpfTempSignal.connect(self.dpfTempUpdateSlot)

    @pyqtSlot(int)
    def rpmUpdateSlot(self, value):
        if 1500 < value < 2500:
            self.ui.rpmBar.setStyleSheet('QProgressBar::chunk{ background-color: rgb(59, 212, 120); width: 14px; margin: 0.8px;}')
        elif value > 3000:
            self.ui.rpmBar.setStyleSheet('QProgressBar::chunk{ background-color: rgb(255, 106, 108); width: 14px; margin: 0.8px;}')
        else:
            self.ui.rpmBar.setStyleSheet('QProgressBar::chunk{ background-color: rgb(105, 185, 255); width: 14px; margin: 0.8px;}')
        self.ui.rpmBar.setValue(value)

    @pyqtSlot(int)
    def speedUpdateSlot(self, value):
        del self.speedFilter[0]
        self.speedFilter.append(value)
        self.ui.speedSpin.setValue(int(statistics.mean(self.speedFilter) * 1.04))

    @pyqtSlot(int)
    def tempUpdateSlot(self, value):
        self.ui.tempBar.setValue(value)

    @pyqtSlot(int)
    def loadUpdateSlot(self, value):
        self.ui.loadBar.setValue(value)

    @pyqtSlot(float, bool)
    def dpfDistUpdateSlot(self, value, dpfEnabled):
        self.ui.dpfDistSpin.setValue(value)
        self.ui.dpfEnabled.setEnabled(dpfEnabled)
        print(dpfEnabled)

    @pyqtSlot(float)
    def dpfTempUpdateSlot(self, value):
        self.ui.dpfTempSpin.setValue(value)

def dpfDataProcess(messages):
    btarr = messages[0].data
    print('@@@@@@@DPF Data Parse Test@@@@@@@')
    for idx, bt in enumerate(btarr):
        #print('{}/{} : {}'.format(idx, len(btarr), hex(bt)))
        print(hex(bt), end='  ')
        if idx % 8 == 0:
            print('')
    print('@@@@@@@DPF Data Parse END@@@@@@@@')
    dpfEnabled = True if btarr[7] == 4 else False
    btarr = btarr[56:59]
    v = bytes_to_int(btarr)
    return (v / 1000) * Unit.kilometer, dpfEnabled

class OBDWorker(QThread):
    rpmSignal = pyqtSignal(int)
    speedSignal = pyqtSignal(int)
    tempSignal = pyqtSignal(int)
    loadSignal = pyqtSignal(int)
    dpfDistSignal = pyqtSignal(float, bool)
    dpfTempSignal = pyqtSignal(float)
    def __init__(self):
        QThread.__init__(self)
        self.connection = obd.OBD() # auto-connects to USB or RF port

        # OBD2 Data
        self.RPM = obd.commands.RPM
        self.SPEED = obd.commands.SPEED
        self.TEMP = obd.commands.COOLANT_TEMP
        self.ENGINE_LOAD = obd.commands.ENGINE_LOAD
        self.DPF_DISTANCE = OBDCommand('DPF', 'DPF INFO', b"2103", 0, dpfDataProcess)
        self.DPF_TEMP = obd.commands.CATALYST_TEMP_B1S2

        self.loop_count = 0

    def run(self):
        # Test Code
        while True:
            rpm = self.connection.query(self.RPM)
            self.rpmSignal.emit(rpm.value.magnitude)

            speed = self.connection.query(self.SPEED)
            self.speedSignal.emit(speed.value.magnitude)

            temp = self.connection.query(self.TEMP)
            self.tempSignal.emit(temp.value.magnitude)

            engine_load = self.connection.query(self.ENGINE_LOAD)
            self.loadSignal.emit(engine_load.value.magnitude)


            if self.loop_count % 50 == 0:
                dpf_temp = self.connection.query(self.DPF_TEMP)
                self.dpfTempSignal.emit(dpf_temp.value.magnitude)

                dpf_distance = self.connection.query(self.DPF_DISTANCE, force=True)
                self.dpfDistSignal.emit(dpf_distance.value[0].magnitude, dpf_distance.value[1])

            self.loop_count = self.loop_count + 1


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    w = PiHud()
    w.ui.showFullScreen()
    sys.exit(app.exec())
