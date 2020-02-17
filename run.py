import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 450]


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.ll = "37.530887,55.703118"
        self.ll = "85.0,85.0"
        # self.spn = "0.002,0.002"
        self.spn = "85.0,85.0"
        self.l = "map"
        self.initUI()
        self.update_image()

    def update_image(self):
        self.loading.show()
        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)
        self.loading.hide()

    def keyPressEvent(self, event):
        max_spn = 85.0
        min_spn = 0.001
        delta_move_up_down = 85 / 180
        delta_move_left_right = 1
        if event.key() == Qt.Key_PageUp:
            delta = 0.5
            data = list(map(float, self.spn.split(',')))
            data[0] *= (1 + delta)
            data[1] *= (1 + delta)
            if data[0] > max_spn:
                data[0] = max_spn
            if data[1] > max_spn:
                data[1] = max_spn
            self.spn = ','.join(list(map(str, data)))
        elif event.key() == Qt.Key_PageDown:
            delta = 0.5
            data = list(map(float, self.spn.split(',')))
            data[0] *= (1 - delta)
            data[1] *= (1 - delta)
            if data[0] < min_spn:
                data[0] = min_spn
            if data[1] < min_spn:
                data[1] = min_spn
            self.spn = ','.join(list(map(str, data)))
        elif event.key() == Qt.Key_Up:
            data = list(map(float, self.ll.split(',')))
            spn = list(map(float, self.spn.split(',')))
            data[1] += spn[1] * delta_move_up_down
            if data[1] > 85:
                data[1] = 85
            self.ll = ','.join(list(map(str, data)))
        elif event.key() == Qt.Key_Down:
            data = list(map(float, self.ll.split(',')))
            spn = list(map(float, self.spn.split(',')))
            data[1] -= spn[1] * delta_move_up_down
            if data[1] < -85:
                data[1] = -85
            self.ll = ','.join(list(map(str, data)))
        elif event.key() == Qt.Key_Left:
            data = list(map(float, self.ll.split(',')))
            spn = list(map(float, self.spn.split(',')))
            data[0] -= spn[0] * delta_move_left_right
            if data[0] < -179:
                data[0] += 360
            self.ll = ','.join(list(map(str, data)))
        elif event.key() == Qt.Key_Right:
            data = list(map(float, self.ll.split(',')))
            spn = list(map(float, self.spn.split(',')))
            data[0] += spn[0] * delta_move_left_right
            if data[0] > 179:
                data[0] -= 360
            self.ll = ','.join(list(map(str, data)))
        else:
            return

        self.update_image()
        print(f'spn={self.spn}, ll={self.ll}')
    def getImage(self):
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        map_params = {
            "ll": self.ll,
            "spn": self.spn,
            "l": self.l
        }
        response = requests.get(map_api_server, params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(f"{map_api_server}?{'&'.join([f'{key}={val}' for key, val in map_params.items()])}")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        # Изображение
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)

        # Надпись загрузки
        self.loading = LoadingText()

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


class LoadingText(QWidget):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        self.setWindowTitle("Обновление...")
        self.setFixedSize(300, 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
