"""
元数据标注GUI模块
提供用户界面用于输入UI元素的元数据信息

Author: Claude AI Assistant
Version: 1.0
"""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QComboBox, QCheckBox, QTextEdit, QPushButton,
    QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter
from PIL.ImageQt import ImageQt

from json_generator import JSONGenerator


class AnnotationWindow(QWidget):
    """元数据标注窗口"""

    # 元素类型选项
    ELEMENT_TYPES = [
        "button", "input_field", "textarea", "dropdown",
        "checkbox", "radio_button", "menu_item", "tab",
        "dialog", "window", "icon", "label"
    ]

    # 默认动作选项
    DEFAULT_ACTIONS = [
        "click", "double_click", "right_click",
        "hover", "input_text", "select_option"
    ]

    def __init__(self, capture_data):
        super().__init__()
        self.capture_data = capture_data
        self.json_generator = JSONGenerator()

        # 存储表单控件的字典
        self.form_widgets = {}

        self.setup_ui()
        self.setup_window()

        logging.info("标注窗口已创建")

    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("Element Digitizer - 元素标注")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        # 窗口居中
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        # 确保窗口在最前面
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        self.raise_()
        self.activateWindow()

    def setup_ui(self):
        """设置用户界面"""
        # 创建主布局
        main_layout = QHBoxLayout(self)

        # 左侧：截图预览区域
        self.setup_preview_area(main_layout)

        # 右侧：表单区域
        self.setup_form_area(main_layout)

    def setup_preview_area(self, parent_layout):
        """设置截图预览区域"""
        preview_group = QGroupBox("截图预览")
        preview_layout = QVBoxLayout(preview_group)

        # 创建预览标签
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                background-color: #f9f9f9;
                min-height: 200px;
            }
        """)

        # 显示截图
        self.display_screenshot()

        preview_layout.addWidget(self.preview_label)

        # 显示坐标信息
        coords_label = QLabel(f"坐标: {self.capture_data.bounding_box}")
        coords_label.setStyleSheet("font-weight: bold; color: #666;")
        preview_layout.addWidget(coords_label)

        parent_layout.addWidget(preview_group)

    def display_screenshot(self):
        """显示截图预览"""
        try:
            # 将PIL图像转换为Qt格式
            qt_image = ImageQt(self.capture_data.screenshot_image)
            pixmap = QPixmap.fromImage(qt_image)

            # 缩放图像以适应预览区域，保持比例
            scaled_pixmap = pixmap.scaled(
                400, 300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.preview_label.setPixmap(scaled_pixmap)

        except Exception as e:
            logging.error(f"显示截图失败: {e}")
            self.preview_label.setText("无法显示截图")

    def setup_form_area(self, parent_layout):
        """设置表单区域"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # 创建表单容器
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)

        # 基本信息组
        self.create_basic_info_group(form_layout)

        # 位置信息组
        self.create_location_info_group(form_layout)

        # 状态信息组
        self.create_state_info_group(form_layout)

        # 动作信息组
        self.create_action_info_group(form_layout)

        # 元数据信息组
        self.create_metadata_info_group(form_layout)

        # 控制按钮
        self.create_control_buttons(form_layout)

        # 添加弹性空间
        form_layout.addStretch()

        scroll_area.setWidget(form_container)
        parent_layout.addWidget(scroll_area)

    def create_basic_info_group(self, parent_layout):
        """创建基本信息组"""
        group = QGroupBox("基本信息")
        layout = QGridLayout(group)

        # element_id (必填)
        layout.addWidget(QLabel("元素ID *:"), 0, 0)
        self.form_widgets['element_id'] = QLineEdit()
        self.form_widgets['element_id'].setPlaceholderText("例: main_menu_button")
        layout.addWidget(self.form_widgets['element_id'], 0, 1)

        # element_name
        layout.addWidget(QLabel("元素名称:"), 1, 0)
        self.form_widgets['element_name'] = QLineEdit()
        self.form_widgets['element_name'].setPlaceholderText("例: 主菜单按钮")
        layout.addWidget(self.form_widgets['element_name'], 1, 1)

        # element_type
        layout.addWidget(QLabel("元素类型:"), 2, 0)
        self.form_widgets['element_type'] = QComboBox()
        self.form_widgets['element_type'].addItems(self.ELEMENT_TYPES)
        layout.addWidget(self.form_widgets['element_type'], 2, 1)

        # parent_element_id
        layout.addWidget(QLabel("父元素ID:"), 3, 0)
        self.form_widgets['parent_element_id'] = QLineEdit()
        self.form_widgets['parent_element_id'].setPlaceholderText("可选")
        layout.addWidget(self.form_widgets['parent_element_id'], 3, 1)

        # module_name (用于文件路径)
        layout.addWidget(QLabel("模块名称:"), 4, 0)
        self.form_widgets['module_name'] = QLineEdit()
        self.form_widgets['module_name'].setText("default")
        self.form_widgets['module_name'].setPlaceholderText("用于文件目录分类")
        layout.addWidget(self.form_widgets['module_name'], 4, 1)

        parent_layout.addWidget(group)

    def create_location_info_group(self, parent_layout):
        """创建位置信息组"""
        group = QGroupBox("位置信息")
        layout = QGridLayout(group)

        # anchor_id
        layout.addWidget(QLabel("锚点ID:"), 0, 0)
        self.form_widgets['anchor_id'] = QLineEdit()
        self.form_widgets['anchor_id'].setPlaceholderText("可选：用于定位的锚点元素ID")
        layout.addWidget(self.form_widgets['anchor_id'], 0, 1)

        parent_layout.addWidget(group)

    def create_state_info_group(self, parent_layout):
        """创建状态信息组"""
        group = QGroupBox("状态信息")
        layout = QGridLayout(group)

        # is_enabled
        self.form_widgets['is_enabled'] = QCheckBox("元素已启用")
        self.form_widgets['is_enabled'].setChecked(True)
        layout.addWidget(self.form_widgets['is_enabled'], 0, 0)

        # is_visible
        self.form_widgets['is_visible'] = QCheckBox("元素可见")
        self.form_widgets['is_visible'].setChecked(True)
        layout.addWidget(self.form_widgets['is_visible'], 0, 1)

        # tooltip
        layout.addWidget(QLabel("工具提示:"), 1, 0)
        self.form_widgets['tooltip'] = QLineEdit()
        self.form_widgets['tooltip'].setPlaceholderText("鼠标悬停时显示的提示文本")
        layout.addWidget(self.form_widgets['tooltip'], 1, 1)

        parent_layout.addWidget(group)

    def create_action_info_group(self, parent_layout):
        """创建动作信息组"""
        group = QGroupBox("动作信息")
        layout = QGridLayout(group)

        # default_action
        layout.addWidget(QLabel("默认动作 *:"), 0, 0)
        self.form_widgets['default_action'] = QComboBox()
        self.form_widgets['default_action'].addItems(self.DEFAULT_ACTIONS)
        layout.addWidget(self.form_widgets['default_action'], 0, 1)

        # expected_outcome_desc
        layout.addWidget(QLabel("预期结果描述:"), 1, 0)
        self.form_widgets['expected_outcome_desc'] = QTextEdit()
        self.form_widgets['expected_outcome_desc'].setMaximumHeight(80)
        self.form_widgets['expected_outcome_desc'].setPlaceholderText("描述执行此动作后的预期结果...")
        layout.addWidget(self.form_widgets['expected_outcome_desc'], 1, 1)

        parent_layout.addWidget(group)

    def create_metadata_info_group(self, parent_layout):
        """创建元数据信息组"""
        group = QGroupBox("元数据信息")
        layout = QGridLayout(group)

        # software_version
        layout.addWidget(QLabel("软件版本 *:"), 0, 0)
        self.form_widgets['software_version'] = QLineEdit()
        self.form_widgets['software_version'].setPlaceholderText("例: v1.2.3")
        layout.addWidget(self.form_widgets['software_version'], 0, 1)

        # author
        layout.addWidget(QLabel("作者 *:"), 1, 0)
        self.form_widgets['author'] = QLineEdit()
        self.form_widgets['author'].setPlaceholderText("标注人员姓名")
        layout.addWidget(self.form_widgets['author'], 1, 1)

        parent_layout.addWidget(group)

    def create_control_buttons(self, parent_layout):
        """创建控制按钮"""
        button_layout = QHBoxLayout()

        # 生成并保存JSON按钮
        self.save_button = QPushButton("生成并保存JSON")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.save_button.clicked.connect(self.save_json)

        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c1180d;
            }
        """)
        self.cancel_button.clicked.connect(self.close)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        parent_layout.addLayout(button_layout)

    def validate_form(self):
        """验证表单数据"""
        errors = []

        # 检查必填字段
        required_fields = {
            'element_id': '元素ID',
            'software_version': '软件版本',
            'author': '作者'
        }

        for field, label in required_fields.items():
            value = self.form_widgets[field].text().strip()
            if not value:
                errors.append(f"{label} 不能为空")

        # 验证element_id格式 (只能包含小写字母、数字和下划线)
        element_id = self.form_widgets['element_id'].text().strip()
        if element_id:
            import re
            if not re.match(r'^[a-z0-9_]+$', element_id):
                errors.append("元素ID只能包含小写字母、数字和下划线")

        return errors

    def collect_form_data(self):
        """收集表单数据"""
        data = {}

        # 基本字符串字段
        string_fields = [
            'element_id', 'element_name', 'parent_element_id',
            'anchor_id', 'tooltip', 'expected_outcome_desc',
            'software_version', 'author', 'module_name'
        ]

        for field in string_fields:
            value = self.form_widgets[field].text().strip() if hasattr(self.form_widgets[field], 'text') else self.form_widgets[field].toPlainText().strip()
            data[field] = value if value else None

        # 下拉框字段
        data['element_type'] = self.form_widgets['element_type'].currentText()
        data['default_action'] = self.form_widgets['default_action'].currentText()

        # 复选框字段
        data['is_enabled'] = self.form_widgets['is_enabled'].isChecked()
        data['is_visible'] = self.form_widgets['is_visible'].isChecked()

        # 处理空值
        if not data['parent_element_id']:
            data['parent_element_id'] = None
        if not data['anchor_id']:
            data['anchor_id'] = None
        if not data['tooltip']:
            data['tooltip'] = None
        if not data['expected_outcome_desc']:
            data['expected_outcome_desc'] = None
        if not data['module_name']:
            data['module_name'] = 'default'

        return data

    def save_json(self):
        """保存JSON文件"""
        try:
            # 验证表单
            errors = self.validate_form()
            if errors:
                error_msg = "请修正以下错误:\n\n" + "\n".join(f"• {error}" for error in errors)
                QMessageBox.warning(self, "表单验证失败", error_msg)
                return

            # 收集表单数据
            form_data = self.collect_form_data()

            # 使用JSON生成器保存数据
            success, message = self.json_generator.generate_and_save(
                form_data,
                self.capture_data
            )

            if success:
                # 显示成功消息
                QMessageBox.information(self, "保存成功",
                    f"元素数据已成功保存!\n\n{message}")

                # 清空表单
                self.clear_form()

                logging.info("JSON文件保存成功")

            else:
                # 显示错误消息
                QMessageBox.critical(self, "保存失败",
                    f"保存失败:\n{message}")

                logging.error(f"JSON文件保存失败: {message}")

        except Exception as e:
            error_msg = f"保存过程中发生错误: {str(e)}"
            QMessageBox.critical(self, "保存失败", error_msg)
            logging.error(f"保存JSON文件时发生异常: {e}")
            import traceback
            logging.error(traceback.format_exc())

    def clear_form(self):
        """清空表单"""
        try:
            # 清空文本字段
            text_fields = [
                'element_id', 'element_name', 'parent_element_id',
                'anchor_id', 'tooltip', 'software_version', 'author'
            ]

            for field in text_fields:
                if field in self.form_widgets:
                    self.form_widgets[field].clear()

            # 清空文本区域
            if 'expected_outcome_desc' in self.form_widgets:
                self.form_widgets['expected_outcome_desc'].clear()

            # 重置下拉框到第一项
            if 'element_type' in self.form_widgets:
                self.form_widgets['element_type'].setCurrentIndex(0)
            if 'default_action' in self.form_widgets:
                self.form_widgets['default_action'].setCurrentIndex(0)

            # 重置复选框
            if 'is_enabled' in self.form_widgets:
                self.form_widgets['is_enabled'].setChecked(True)
            if 'is_visible' in self.form_widgets:
                self.form_widgets['is_visible'].setChecked(True)

            # 重置模块名称为default
            if 'module_name' in self.form_widgets:
                self.form_widgets['module_name'].setText('default')

            logging.debug("表单已清空")

        except Exception as e:
            logging.error(f"清空表单时发生错误: {e}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        logging.debug("标注窗口已关闭")
        event.accept()