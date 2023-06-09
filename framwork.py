import sys
import os,read
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox,QDialog
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QLabel, QLineEdit, QPushButton, QSplitter
from PyQt5.QtCore import QSettings,Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtCore
import analyze
from PyQt5.QtCore import QThread, pyqtSignal


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.search_thread = None

        # 设置窗口大小
        self.setGeometry(100, 100, 900, 600)
        self.setFixedSize(self.size())  # 锁定窗口大小

        # 创建菜单栏
        menubar = self.menuBar()

        # 创建文件菜单
        file_menu = menubar.addMenu("文件")
        folder_action = QAction("选择文件夹", self)
        folder_action.triggered.connect(self.select_folder)
        file_menu.addAction(folder_action)

        # 创建搜索菜单
        search_menu = menubar.addMenu("搜索")
        search_action = QAction("关键词搜索", self)
        search_menu.addAction(search_action)

        # 创建帮助菜单
        help_menu = menubar.addMenu("帮助")
        help_action = QAction("查看帮助", self)
        help_menu.addAction(help_action)

        # 创建主窗口的中心部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 创建上方区域的部件
        self.top_widget = QWidget(central_widget)
        self.top_widget.setGeometry(20, 10, self.width(), self.height() // 6+10)

        # 创建上方区域的部件
        self.label_widget = QLabel(self.top_widget)
        self.label_widget.setGeometry(10, 10, self.top_widget.width()-180, 60)
        self.label_widget.setAlignment(Qt.AlignCenter)
        self.label_widget.setStyleSheet("QLabel { border: 1px solid black; }")
        self.label_widget.setWordWrap(True)  # 启用自动换行

        self.button_path = QPushButton("修改", self.top_widget)
        self.button_path.setGeometry(self.top_widget.width()-158,8, 104, 64)
        self.button_path.clicked.connect(folder_action.trigger)

        # 创建下方区域的部件
        self.bottom_widget = QWidget(central_widget)
        self.bottom_widget.setGeometry(20, self.height() // 6 - 10, self.width() - 20, self.height() * 5 // 6 - 30)

        # 添加文件列表部件到下方区域
        
        self.file_list_widget = QScrollArea(self.bottom_widget)
        self.file_list_widget.setGeometry(10, 0, 400, self.bottom_widget.height() - 20)

        self.file_list_label_widget = QWidget(self.file_list_widget)
        self.file_list_label_layout = QVBoxLayout(self.file_list_label_widget)
        self.file_list_label_layout.setContentsMargins(0, 0, 0, 0)

        self.file_list_label = QLabel(self.file_list_label_print())
        self.file_list_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.file_list_label_layout.addWidget(self.file_list_label)
        self.file_list_widget.setWidget(self.file_list_label_widget)

        # 添加文本输入框和按钮到右侧区域
        self.text_input1 = QLineEdit(self.bottom_widget)
        self.button1 = QPushButton("AND", self.bottom_widget)
        self.text_input2 = QLineEdit(self.bottom_widget)
        self.button2 = QPushButton("AND", self.bottom_widget)
        self.text_input3 = QLineEdit(self.bottom_widget)
        self.button3 = QPushButton("搜索", self.bottom_widget)
        self.button4 = QPushButton("重置", self.bottom_widget)

        # 设置部件的位置和大小
        self.text_input1.setGeometry(420, 0, self.bottom_widget.width() - 450, 60)
        self.button1.setGeometry(420, 70, 100, 60)
        self.text_input2.setGeometry(520, 70, self.bottom_widget.width() - 550, 60)
        self.button2.setGeometry(420, 140, 100, 60)
        self.text_input3.setGeometry(520, 140, self.bottom_widget.width() - 550, 60)
        self.button3.setGeometry(635, 210, 215, 60)
        self.button4.setGeometry(420, 210, 215, 60)
        
        #设置各个部件功能
        # 按钮1点击事件
        self.button1.clicked.connect(self.toggle_button1)
        # 按钮2点击事件
        self.button2.clicked.connect(self.toggle_button2)
        # 搜索按钮点击事件
        self.button3.clicked.connect(self.generate_new_page)
        # 重置按钮点击事件
        self.button4.clicked.connect(self.reset_inputs)

#这里开始为文件路径相关方法
    def path_cheak(self):
        self.config = QSettings("config.ini", QSettings.IniFormat)
        folder_path = self.config.value("folder_path")
        if folder_path is None or folder_path == "":
            return False
        else:
            return True
    
    def get_path(self):
        self.config = QSettings("config.ini", QSettings.IniFormat)
        folder_path = self.config.value("folder_path")
        return folder_path

    def config_cheak(self):
        # 解析配置文件
        self.config = QSettings("config.ini", QSettings.IniFormat)
        folder_path = self.config.value("folder_path")
        if folder_path is None or folder_path == "":
            reply = QMessageBox.question(self, "文件夹路径未设置", "文件夹路径未设置，是否前往设置？", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.select_folder()
        else:
            self.folder_path = folder_path
            self.update_folder_path()  # 更新 label_widget 的文本内容
            self.update_files()

    def select_folder(self):
        # 实现选择文件夹的逻辑
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", options=QFileDialog.ShowDirsOnly)
        if folder_path:
            self.folder_path = folder_path
            self.config.setValue("folder_path", folder_path)
            self.update_folder_path()  # 更新 label_widget 的文本内容
            self.update_files()
    
    def update_folder_path(self):
        self.label_widget.setText(f"当前文件夹位置: {self.folder_path}")

#这里开始为更新文件夹内文件内容字符串
    def set_files(self):
        self.file_list_label = QLabel(self.file_list_label_print(), self.bottom_widget)
        
    def update_files(self):    
        new_text = self.file_list_label_print()
        self.file_list_label.setText(new_text)
        
    def file_list_label_print(self):
        list_files = read.sort_files(read.get_file_names(self.get_path()))
        string = ""
        for list_file in list_files:
            string = string + list_file + "\n"
        return string 


#这里开始为搜索框按钮功能方法
    def reset_inputs(self):
        self.text_input1.clear()
        self.text_input2.clear()
        self.text_input3.clear()
        print('reset')
        

    def generate_new_page(self):
        # 创建搜索中对话框
        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("搜索中")
        progress_dialog.setText("请稍后...")
        progress_dialog.setStandardButtons(QMessageBox.NoButton)
        progress_dialog.show()
        print('dialog')
        input1 = self.text_input1.text()
        input2 = self.text_input2.text()
        input3 = self.text_input3.text()
        if self.button1.text() == "AND":
            button1_state = True
        else:
            button1_state = False
        if self.button2.text() == "AND":
            button2_state = True
        else:
            button2_state = False
        search_list = [[input1, True], [input2, button1_state], [input3, button2_state]]
        # 创建并启动搜索线程
        QtCore.QCoreApplication.processEvents()
        self.search_thread = SearchThread(search_list, self.get_path())
        self.search_thread.search_completed.connect(self.handle_search_completed)
        self.search_thread.start()
        print('search')
        # 关闭进度对话框
        progress_dialog.close()
        print('dialog_close')

    def handle_search_completed(self, search_results):
        second_page = SecondPage(search_results)
        second_page.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        second_page.exec_()

    def closeEvent(self, event):
        # 确保在关闭主窗口时停止搜索线程
        if self.search_thread is not None:
            self.search_thread.quit()
            self.search_thread.wait()
        event.accept()

    def toggle_button1(self):
        if self.button1.text() == "AND":
            self.button1.setText("NOT")
        else:
            self.button1.setText("AND")

    def toggle_button2(self):
        if self.button2.text() == "AND":
            self.button2.setText("NOT")
        else:
            self.button2.setText("AND")

class SearchThread(QThread):
    search_completed = pyqtSignal(list)

    def __init__(self, search_list, folder_path):
        super().__init__()
        self.search_list = search_list
        self.folder_path = folder_path

    def run(self):
        search_results = analyze.search(self.search_list, self.folder_path)
        self.search_completed.emit(search_results)

class SecondPage(QDialog):
    def __init__(self, inputs):
        super().__init__()
        self.setWindowTitle("第二个程序界面")
        self.setGeometry(100, 100, 1200, 900)
    



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    main_window.config_cheak()
    sys.exit(app.exec_())