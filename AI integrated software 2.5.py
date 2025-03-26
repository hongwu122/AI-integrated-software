import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QComboBox,QLineEdit, QListWidget, QTextEdit, QLabel, QSizePolicy, QSplitter
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap

# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class AIBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("小鸿武的 AI 空间")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("icons/app_icon.png"))  # 设置软件运行图标

        self.url_list_file = "config/ai_urls.json"
        self.prompt_list_file = "config/ai_prompts.txt"
        self.url_dict = self.load_urls()
        self.prompt_list = self.load_prompts()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout()

        # 左侧主界面
        left_layout = QVBoxLayout()

        # 顶部 - 选择AI网站
        self.url_selector = QComboBox()
        self.url_selector.setStyleSheet("font-size: 16px; padding: 5px;")
        self.update_url_selector()
        self.url_selector.currentIndexChanged.connect(self.load_selected_url)

        # 网址Logo和名称
        self.site_logo = QLabel()
        self.site_logo.setFixedSize(32, 32)  # 设置Logo大小
        self.site_name = QLabel("网站名称")
        self.site_name.setStyleSheet("font-size: 16px; font-weight: bold; margin-left: 10px;")

        # 中间区域布局
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.site_logo)
        middle_layout.addWidget(self.site_name)

        top_layout = QHBoxLayout()
        # top_layout.addWidget(QLabel("选择AI网站:"))
        top_layout.addLayout(middle_layout)  # 添加网站Logo和名称
        top_layout.addWidget(self.url_selector)

        # 网页显示区域
        self.web_view = QWebEngineView()
        self.web_page = QWebEnginePage()  # 创建 QWebEnginePage

        self.web_profile = self.web_page.profile()  # 获取 QWebEngineProfile
        # self.web_profile.setHttpUserAgent(USER_AGENT)  # 设置 User-Agent

        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        left_layout.addLayout(top_layout)
        left_layout.addWidget(self.web_view, stretch=1)

        # 右侧设置区域
        self.right_widget = QWidget()
        right_layout = QVBoxLayout()

        # 设置按钮（切换显示设置区域）
        self.settings_button = QPushButton(" 设置") # ⚙
        self.settings_button.setIcon(QIcon("icons/settings.png"))
        self.settings_button.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        self.settings_button.clicked.connect(self.toggle_settings)
        top_layout.addWidget(self.settings_button)

        # 网址管理
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入AI网址并回车访问...")

        self.load_button = QPushButton("加载AI网站")
        self.load_button.clicked.connect(self.load_custom_url)

        self.save_url_button = QPushButton("保存网址")
        self.save_url_button.clicked.connect(self.save_url)

        self.delete_url_button = QPushButton("删除网址")
        self.delete_url_button.clicked.connect(self.delete_url)

        # 提示词管理
        self.prompt_selector = QListWidget()
        self.prompt_selector.setStyleSheet("font-size: 14px;")
        self.update_prompt_list()
        self.prompt_selector.itemClicked.connect(self.use_prompt)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("输入新的提示词...")

        self.save_prompt_button = QPushButton(" 保存提示词")
        self.save_prompt_button.setIcon(QIcon("icons/save.png"))
        self.save_prompt_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        self.save_prompt_button.clicked.connect(self.save_prompt)

        self.delete_prompt_button = QPushButton(" 删除提示词")
        self.delete_prompt_button.setIcon(QIcon("icons/delete.png"))
        self.delete_prompt_button.setStyleSheet("background-color: #F44336; color: white; padding: 5px;")
        self.delete_prompt_button.clicked.connect(self.delete_prompt)

        # 设置界面布局
        right_layout.addWidget(QLabel("网址管理:"))
        right_layout.addWidget(self.url_input)
        right_layout.addWidget(self.load_button)
        right_layout.addWidget(self.save_url_button)
        right_layout.addWidget(self.delete_url_button)
        right_layout.addWidget(QLabel("常用提示词:"))
        right_layout.addWidget(self.prompt_selector)
        right_layout.addWidget(self.prompt_input)
        right_layout.addWidget(self.save_prompt_button)
        right_layout.addWidget(self.delete_prompt_button)

        # 监听 self.prompt_selector 的 itemClicked 事件
        self.prompt_selector.itemClicked.connect(self.copy_prompt_to_clipboard)  # 绑定点击事件

        self.right_widget.setLayout(right_layout)
        self.right_widget.setVisible(False)

        # 拆分区域
        splitter = QSplitter()
        left_container = QWidget()
        left_container.setLayout(left_layout)
        splitter.addWidget(left_container)
        splitter.addWidget(self.right_widget)

        main_layout.addWidget(splitter)
        self.central_widget.setLayout(main_layout)

        self.load_selected_url()

    def copy_prompt_to_clipboard(self, item):
        """点击列表项时，将其文本复制到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(item.text())  # 复制文本
        self.statusBar().showMessage(f"已复制: {item.text()}", 2000)  # 在状态栏显示提示信息

    def toggle_settings(self):
        self.right_widget.setVisible(not self.right_widget.isVisible())

    def load_selected_url(self):
        url = self.url_selector.currentText()
        self.web_view.setUrl(QUrl(url))

        # 读取网站名称
        site_name = self.url_dict.get(url, "未知网站")
        self.site_name.setText(site_name)

        # 读取 Logo 文件
        logo_path = f"icons/{site_name}.png"
        if os.path.exists(logo_path):
            self.site_logo.setPixmap(QPixmap(logo_path).scaled(32, 32, Qt.KeepAspectRatio))
        else:
            self.site_logo.clear()

    def load_custom_url(self):
        url = self.url_input.text()
        self.web_view.setUrl(QUrl(url if url.startswith("http") else "https://" + url))

    def save_url(self):
        url = self.url_input.text()
        if url and url not in self.url_dict:
            self.url_dict[url] = "自定义网址"
            self.save_urls()
            self.update_url_selector()

    def delete_url(self):
        url = self.url_selector.currentText()
        if url in self.url_dict:
            del self.url_dict[url]
            self.save_urls()
            self.update_url_selector()

    def save_urls(self):
        with open(self.url_list_file, "w", encoding="utf-8") as f:
            json.dump(self.url_dict, f, ensure_ascii=False, indent=4)

    def load_urls(self):
        return json.load(open(self.url_list_file, "r", encoding="utf-8")) if os.path.exists(self.url_list_file) else {}

    def update_url_selector(self):
        self.url_selector.clear()
        self.url_selector.addItems(self.url_dict.keys())

    def load_prompts(self):
        return open(self.prompt_list_file, "r", encoding="utf-8").read().splitlines() if os.path.exists(
            self.prompt_list_file) else []

    def save_prompt(self):
        prompt = self.prompt_input.toPlainText()
        if prompt and prompt not in self.prompt_list:
            self.prompt_list.append(prompt)
            open(self.prompt_list_file, "w", encoding="utf-8").write("\n".join(self.prompt_list))
            self.update_prompt_list()

    def delete_prompt(self):
        for item in self.prompt_selector.selectedItems():
            self.prompt_list.remove(item.text())
            open(self.prompt_list_file, "w", encoding="utf-8").write("\n".join(self.prompt_list))
            self.update_prompt_list()

    def update_prompt_list(self):
        self.prompt_selector.clear()
        self.prompt_selector.addItems(self.prompt_list)

    def use_prompt(self, item):
        self.prompt_input.setText(item.text())

    def open_settings(self):
        self.prompt_widget.setVisible(not self.prompt_widget.isVisible())

    # def resizeEvent(self, event):
    #     font_size = max(12, self.width() // 100)
    #     self.setStyleSheet(f"font-size: {font_size}px;")
    #     super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIBrowser()
    window.show()
    sys.exit(app.exec_())
