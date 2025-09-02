#!/usr/bin/env python3
"""
Element Digitizer - UI元素数字化标注工具
主程序入口点

Author: Claude AI Assistant
Version: 1.0
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QThread, pyqtSignal
from pynput import keyboard
import traceback

from capture_module import CaptureController
from annotation_gui import AnnotationWindow


class GlobalHotkeyThread(QThread):
    """全局热键监听线程"""
    hotkey_pressed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        """监听 Ctrl+Shift+C 热键"""
        try:
            with keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+c': self.on_hotkey_pressed
            }):
                while self.running:
                    self.msleep(100)
        except Exception as e:
            logging.error(f"热键监听线程错误: {e}")
            
    def on_hotkey_pressed(self):
        """热键被按下时的回调"""
        self.hotkey_pressed.emit()
        
    def stop(self):
        """停止热键监听"""
        self.running = False


class ElementDigitizerApp:
    """主应用程序类"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # 设置日志
        self.setup_logging()
        
        # 初始化组件
        self.capture_controller = None
        self.annotation_window = None
        self.hotkey_thread = None
        
        # 创建系统托盘
        self.setup_system_tray()
        
        # 启动热键监听
        self.start_hotkey_listener()
        
        logging.info("Element Digitizer 已启动")
        
    def setup_logging(self):
        """设置日志系统"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('element_digitizer.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
    def setup_system_tray(self):
        """设置系统托盘图标和菜单"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logging.error("系统托盘不可用")
            sys.exit(1)
            
        # 创建托盘图标 (使用默认图标)
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 开始捕获动作
        capture_action = QAction("开始捕获 (Ctrl+Shift+C)", self.app)
        capture_action.triggered.connect(self.start_capture)
        tray_menu.addAction(capture_action)
        
        tray_menu.addSeparator()
        
        # 退出动作
        quit_action = QAction("退出", self.app)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("Element Digitizer - UI元素标注工具")
        self.tray_icon.show()
        
        # 托盘图标点击事件
        self.tray_icon.activated.connect(self.tray_icon_clicked)
        
    def tray_icon_clicked(self, reason):
        """托盘图标被点击"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.start_capture()
            
    def start_hotkey_listener(self):
        """启动全局热键监听线程"""
        self.hotkey_thread = GlobalHotkeyThread()
        self.hotkey_thread.hotkey_pressed.connect(self.start_capture)
        self.hotkey_thread.start()
        
    def start_capture(self):
        """开始屏幕捕获模式"""
        try:
            logging.info("启动屏幕捕获模式")
            
            # 如果已经有捕获窗口在运行，先关闭它
            if self.capture_controller:
                self.capture_controller.close()
                
            # 创建新的捕获控制器
            self.capture_controller = CaptureController()
            self.capture_controller.capture_completed.connect(self.on_capture_completed)
            self.capture_controller.show()
            
        except Exception as e:
            logging.error(f"启动捕获模式失败: {e}")
            logging.error(traceback.format_exc())
            
    def on_capture_completed(self, capture_data):
        """捕获完成回调"""
        try:
            logging.info("屏幕捕获完成，打开标注窗口")
            
            # 关闭捕获窗口
            if self.capture_controller:
                self.capture_controller.close()
                self.capture_controller = None
                
            # 打开标注窗口
            if self.annotation_window:
                self.annotation_window.close()
                
            self.annotation_window = AnnotationWindow(capture_data)
            self.annotation_window.show()
            
        except Exception as e:
            logging.error(f"处理捕获完成事件失败: {e}")
            logging.error(traceback.format_exc())
            
    def quit_application(self):
        """退出应用程序"""
        logging.info("正在退出 Element Digitizer")
        
        # 停止热键监听
        if self.hotkey_thread:
            self.hotkey_thread.stop()
            self.hotkey_thread.wait(1000)  # 等待1秒
            
        # 关闭所有窗口
        if self.capture_controller:
            self.capture_controller.close()
        if self.annotation_window:
            self.annotation_window.close()
            
        # 退出应用
        self.app.quit()
        
    def run(self):
        """运行应用程序"""
        try:
            return self.app.exec()
        except KeyboardInterrupt:
            logging.info("收到键盘中断信号")
            self.quit_application()
            return 0
        except Exception as e:
            logging.error(f"应用程序运行时发生错误: {e}")
            logging.error(traceback.format_exc())
            return 1


def main():
    """主函数"""
    try:
        # 确保必要的目录存在
        os.makedirs("database/ui_elements/screenshots", exist_ok=True)
        os.makedirs("database/ui_elements/default", exist_ok=True)
        
        # 创建并运行应用
        app = ElementDigitizerApp()
        sys.exit(app.run())
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()