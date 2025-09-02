"""
屏幕捕获模块
实现全屏覆盖和矩形框选功能

Author: Claude AI Assistant
Version: 1.0
"""

import logging
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QCursor
import mss
from PIL import Image
import io


class CaptureData:
    """捕获数据容器"""

    def __init__(self, bounding_box, screenshot_image):
        self.bounding_box = bounding_box  # [x1, y1, x2, y2]
        self.screenshot_image = screenshot_image  # PIL Image对象


class CaptureController(QWidget):
    """屏幕捕获控制器"""

    capture_completed = pyqtSignal(object)  # 发送CaptureData对象

    def __init__(self):
        super().__init__()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        self.screen_geometry = None

        self.setup_ui()
        self.setup_screen_capture()

    def setup_ui(self):
        """设置UI界面"""
        # 设置窗口为全屏覆盖层
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # 设置窗口属性
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        # 设置鼠标光标为十字准线
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        # 获取屏幕几何信息
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        self.screen_geometry = screen.geometry()

        logging.info(f"屏幕尺寸: {self.screen_geometry.width()}x{self.screen_geometry.height()}")

    def setup_screen_capture(self):
        """初始化屏幕捕获"""
        self.sct = mss.mss()

    def paintEvent(self, event):
        """绘制事件 - 绘制半透明覆盖层和选择框"""
        painter = QPainter(self)

        # 绘制半透明灰色覆盖层
        overlay_color = QColor(128, 128, 128, 51)  # 20% 不透明度
        painter.fillRect(self.rect(), overlay_color)

        # 如果正在绘制选择框，则绘制红色矩形框
        if self.is_drawing and not self.start_point.isNull() and not self.end_point.isNull():
            # 设置红色画笔
            pen = QPen(QColor(255, 0, 0), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)

            # 计算矩形
            rect = QRect(self.start_point, self.end_point).normalized()

            # 绘制矩形框
            painter.drawRect(rect)

            # 在矩形内部绘制稍微透明的背景，以便更好地看到选择区域
            fill_color = QColor(255, 0, 0, 25)  # 10% 不透明度的红色
            painter.fillRect(rect, fill_color)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = event.position().toPoint()
            self.is_drawing = True
            logging.debug(f"开始绘制选择框: {self.start_point}")

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_drawing:
            self.end_point = event.position().toPoint()
            self.update()  # 触发重绘

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.end_point = event.position().toPoint()
            self.is_drawing = False

            # 执行捕获
            self.perform_capture()

    def keyPressEvent(self, event):
        """键盘事件 - ESC键取消捕获"""
        if event.key() == Qt.Key.Key_Escape:
            logging.info("用户取消了屏幕捕获")
            self.close()

    def perform_capture(self):
        """执行屏幕捕获"""
        try:
            # 计算选择矩形
            rect = QRect(self.start_point, self.end_point).normalized()

            # 检查矩形是否有效
            if rect.width() < 10 or rect.height() < 10:
                logging.warning("选择区域太小，取消捕获")
                self.close()
                return

            # 获取屏幕坐标 (相对于屏幕左上角)
            screen_rect = [
                rect.x(),
                rect.y(),
                rect.x() + rect.width(),
                rect.y() + rect.height()
            ]

            logging.info(f"捕获区域坐标: {screen_rect}")

            # 使用mss进行屏幕截图
            monitor = {
                "top": screen_rect[1],
                "left": screen_rect[0],
                "width": screen_rect[2] - screen_rect[0],
                "height": screen_rect[3] - screen_rect[1]
            }

            # 捕获屏幕区域
            screenshot_mss = self.sct.grab(monitor)

            # 转换为PIL Image
            screenshot_image = Image.frombytes(
                "RGB",
                screenshot_mss.size,
                screenshot_mss.bgra,
                "raw",
                "BGRX"
            )

            logging.info(f"截图尺寸: {screenshot_image.size}")

            # 创建捕获数据对象
            capture_data = CaptureData(screen_rect, screenshot_image)

            # 发送捕获完成信号
            self.capture_completed.emit(capture_data)

        except Exception as e:
            logging.error(f"屏幕捕获失败: {e}")
            import traceback
            logging.error(traceback.format_exc())
            self.close()

    def closeEvent(self, event):
        """窗口关闭事件"""
        logging.debug("屏幕捕获窗口已关闭")
        if hasattr(self, 'sct'):
            self.sct.close()
        event.accept()