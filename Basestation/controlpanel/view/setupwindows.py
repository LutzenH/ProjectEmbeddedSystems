import threading
import time

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox
import sys
from multiprocessing import Process
import controlpanel.view.mainwindow as mainwindow
import controlpanel.view.subwindow as subwindow
import controlpanel.model.units as units


class MakeWindows:
    subwindows = []
    roll_delay = 60
    # mainwin = []
    to_remove_from_subwindows = []

    @staticmethod
    def make_main_window():
        app = QtWidgets.QApplication(sys.argv)
        app.setWindowIcon(QIcon("dashboard_icon.png"))
        MainWindow = QtWidgets.QMainWindow()
        ui = mainwindow.Ui_MainWindow(MainWindow)
        ui.setupUi(MainWindow)
        MainWindow.showMaximized()
        sys.exit(app.exec_())

    @staticmethod
    def make_sub_window(unit):
        SubWindow = QtWidgets.QMainWindow()
        ui = subwindow.Ui_SubWindow()
        ui.setupUi(SubWindow, unit)
        SubWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        MakeWindows.subwindows.append(ui)
        if len(MakeWindows.subwindows) == 1:
            t1 = threading.Thread(target=MakeWindows.update)
            t1.daemon = True
            t1.start()
        return SubWindow

    @staticmethod
    def make_max_error():
        message = QMessageBox()
        message.setWindowTitle("ERROR")
        message.setText("Maximum must be higher then minimum.")
        message.setIcon(QMessageBox.Critical)
        message.exec_()

    @staticmethod
    def make_min_error():
        message = QMessageBox()
        message.setWindowTitle("ERROR")
        message.setText("Minimum must be lower then maximum.")
        message.setIcon(QMessageBox.Critical)
        message.exec_()

    @staticmethod
    def update_light_intensity_inputs():
        for x in MakeWindows.subwindows:
            x.light_intensity_input.setValue(units.Units.get_unit_light_intensity(x.unit))

    @staticmethod
    def update_temp_inputs():
        for x in MakeWindows.subwindows:
            x.temperature_input.setValue(units.Units.get_unit_temp(x.unit))

    @staticmethod
    def update_min_inputs():
        for x in MakeWindows.subwindows:
            x.min_roll_out_input.setValue(units.Units.get_unit_min(x.unit))

    @staticmethod
    def update_max_inputs():
        for x in MakeWindows.subwindows:
            x.max_roll_out_input.setValue(units.Units.get_unit_max(x.unit))

    @staticmethod
    def update():
        while len(MakeWindows.subwindows) > 0:
            for unit in units.Units.units:
                unit.generate_new_data()

            for x in MakeWindows.subwindows:
                try:
                    if x.check_if_module_is_connected():
                        x.subwindow.setEnabled(True)
                        x.update()
                    else:
                        units.Units.units[x.unit].module.open_connection()
                        x.subwindow.setEnabled(False)
                except RuntimeError:
                    MakeWindows.to_remove_from_subwindows.append(x)
                QApplication.processEvents()
            if MakeWindows.roll_delay >= 60:
                results = []
                for x in range(len(units.Units.units)):
                    results.append(units.Units.check_weather_unit(x))
                if "open" in results:
                    MakeWindows.roll_delay = 0
                    for x in range(len(units.Units.units)):
                        units.Units.roll_out_unit(x)
                elif "close" in results:
                    MakeWindows.roll_delay = 0
                    for x in range(len(units.Units.units)):
                        units.Units.roll_in_unit(x)
            MakeWindows.roll_delay += 1
            print(MakeWindows.roll_delay)

            for x in MakeWindows.to_remove_from_subwindows:
                MakeWindows.subwindows.remove(x)
                MakeWindows.to_remove_from_subwindows.clear()
            for x in range(0, 9):
                time.sleep(0.1)
                QApplication.processEvents()
            #time.sleep(1)


if __name__ == '__main__':
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    #units.Units.fill_units()
    #MakeWindows.make_main_window()
    MakeWindows.make_sub_window(1)
