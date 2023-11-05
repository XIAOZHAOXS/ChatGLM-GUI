"""
Author:小赵先生
Date:2023/11/5
Power By Pycharm
"""
import sys
import zhipuai
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal

# Replace 'YOUR_API_KEY' with your actual zhipuai API key
zhipuai.api_key = "YOUR_API_KEY"


class WorkerThread(QThread):
    update_chat_signal = pyqtSignal(str)

    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        try:
            response = zhipuai.model_api.sse_invoke(
                model="chatglm_turbo",
                prompt=[{"role": "user", "content": self.message}],
                top_p=0.7,
                temperature=0.9,
            )

            for event in response.events():
                if event.event == "add":
                    # 直接发射返回的字符数据
                    self.update_chat_signal.emit(event.data)
                elif event.event == "error" or event.event == "interrupted":
                    self.update_chat_signal.emit("Error or interrupted: " + event.data)
                elif event.event == "finish":
                    # 可以选择在这里处理'finish'事件
                    pass
        except Exception as e:
            self.update_chat_signal.emit("Exception: " + str(e))


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('小赵先生的AI助理')

        # Layout
        self.layout = QVBoxLayout()

        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)

        # User input
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("请在这里输入你的问题...")

        # Send button
        self.send_button = QPushButton('发送')
        self.send_button.clicked.connect(self.send_message)

        # Adding widgets to layout
        self.layout.addWidget(self.chat_history)
        self.layout.addWidget(self.user_input)
        self.layout.addWidget(self.send_button)

        # Set layout
        self.setLayout(self.layout)

        # Set window dimensions
        self.setGeometry(100, 100, 400, 500)

        # Set styles
        self.setStyleSheet("""
            QWidget {
                font-size: 16px;
            }
            QTextEdit {
                border: None;
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 200);
                padding: 10px;
            }
            QLineEdit {
                border: None;
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 200);
                padding: 10px;
                margin-bottom: 10px;
            }
            QPushButton {
                border: 2px solid #0078D7;
                border-radius: 10px;
                background-color: #0078D7;
                color: white;
                padding: 10px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #005EA6;
            }
        """)

    def send_message(self):
        message = self.user_input.text()
        self.chat_history.append(f"You: {message}\nAI:")
        self.user_input.clear()

        # Start the worker thread
        self.worker_thread = WorkerThread(message)
        self.worker_thread.update_chat_signal.connect(self.update_chat)
        self.worker_thread.start()

    def update_chat(self, message):
        # 直接追加字符到聊天历史中
        cursor = self.chat_history.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(message)
        self.chat_history.setTextCursor(cursor)
        self.chat_history.ensureCursorVisible()


def main():
    app = QApplication(sys.argv)
    chat_window = ChatWindow()
    chat_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()