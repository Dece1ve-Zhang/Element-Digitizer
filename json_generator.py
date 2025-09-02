"""
JSON生成器模块
负责生成符合UI Element Schema v1.0的JSON文件并保存到指定位置

Author: Claude AI Assistant
Version: 1.0
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path


class JSONGenerator:
    """JSON文件生成器"""

    def __init__(self):
        self.schema_version = "1.0"

    def generate_and_save(self, form_data, capture_data):
        """
        生成JSON数据并保存文件

        Args:
            form_data (dict): 从表单收集的数据
            capture_data (CaptureData): 捕获的屏幕数据

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # 构建JSON数据结构
            json_data = self.build_json_structure(form_data, capture_data)

            # 保存截图文件
            screenshot_success, screenshot_path = self.save_screenshot(
                form_data['element_id'],
                capture_data.screenshot_image
            )

            if not screenshot_success:
                return False, f"截图保存失败: {screenshot_path}"

            # 保存JSON文件
            json_success, json_path = self.save_json_file(form_data, json_data)

            if not json_success:
                return False, f"JSON文件保存失败: {json_path}"

            message = f"文件保存成功:\n• JSON: {json_path}\n• 截图: {screenshot_path}"
            return True, message

        except Exception as e:
            logging.error(f"生成和保存JSON时发生错误: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return False, str(e)

    def build_json_structure(self, form_data, capture_data):
        """
        构建符合UI Element Schema v1.0的JSON数据结构

        Args:
            form_data (dict): 表单数据
            capture_data (CaptureData): 捕获数据

        Returns:
            dict: JSON数据结构
        """
        # 获取当前时间
        current_time = datetime.now().isoformat()

        # 生成截图路径
        screenshot_path = f"database/ui_elements/screenshots/{form_data['element_id']}.png"

        # 构建JSON结构
        json_data = {
            "schema_version": self.schema_version,
            "element_id": form_data['element_id'],
            "element_name": form_data['element_name'] or form_data['element_id'],
            "element_type": form_data['element_type'],
            "parent_element_id": form_data['parent_element_id'],
            "location_info": {
                "screenshot_path": screenshot_path,
                "bounding_box": capture_data.bounding_box
            },
            "state_info": {
                "is_enabled": form_data['is_enabled'],
                "is_visible": form_data['is_visible']
            },
            "action_info": {
                "default_action": form_data['default_action']
            },
            "metadata": {
                "software_version": form_data['software_version'],
                "author": form_data['author'],
                "created_at": current_time,
                "updated_at": current_time
            }
        }

        # 添加可选字段
        if form_data.get('anchor_id'):
            json_data["location_info"]["anchor_id"] = form_data['anchor_id']

        if form_data.get('tooltip'):
            json_data["state_info"]["tooltip"] = form_data['tooltip']

        if form_data.get('expected_outcome_desc'):
            json_data["action_info"]["expected_outcome_desc"] = form_data['expected_outcome_desc']

        return json_data

    def save_screenshot(self, element_id, screenshot_image):
        """
        保存截图文件

        Args:
            element_id (str): 元素ID
            screenshot_image (PIL.Image): 截图图像

        Returns:
            tuple: (success: bool, path_or_error: str)
        """
        try:
            # 确保截图目录存在
            screenshots_dir = Path("database/ui_elements/screenshots")
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件路径
            screenshot_path = screenshots_dir / f"{element_id}.png"

            # 保存PNG文件
            screenshot_image.save(screenshot_path, "PNG", optimize=True)

            logging.info(f"截图已保存: {screenshot_path}")
            return True, str(screenshot_path)

        except Exception as e:
            logging.error(f"保存截图失败: {e}")
            return False, str(e)

    def save_json_file(self, form_data, json_data):
        """
        保存JSON文件

        Args:
            form_data (dict): 表单数据
            json_data (dict): JSON数据结构

        Returns:
            tuple: (success: bool, path_or_error: str)
        """
        try:
            # 获取模块名称
            module_name = form_data.get('module_name', 'default')

            # 确保模块目录存在
            module_dir = Path(f"database/ui_elements/{module_name}")
            module_dir.mkdir(parents=True, exist_ok=True)

            # 生成JSON文件路径
            json_path = module_dir / f"{form_data['element_id']}.json"

            # 保存JSON文件 (格式化，使用2个空格缩进)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            logging.info(f"JSON文件已保存: {json_path}")
            return True, str(json_path)

        except Exception as e:
            logging.error(f"保存JSON文件失败: {e}")
            return False, str(e)

    def validate_json_structure(self, json_data):
        """
        验证JSON数据结构是否符合Schema

        Args:
            json_data (dict): JSON数据

        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        errors = []

        # 检查必需字段
        required_fields = [
            "schema_version", "element_id", "element_name", "element_type",
            "location_info", "state_info", "action_info", "metadata"
        ]

        for field in required_fields:
            if field not in json_data:
                errors.append(f"缺少必需字段: {field}")

        # 检查location_info子字段
        if "location_info" in json_data:
            location_info = json_data["location_info"]
            required_location_fields = ["screenshot_path", "bounding_box"]

            for field in required_location_fields:
                if field not in location_info:
                    errors.append(f"location_info缺少必需字段: {field}")

            # 检查bounding_box格式
            if "bounding_box" in location_info:
                bbox = location_info["bounding_box"]
                if not isinstance(bbox, list) or len(bbox) != 4:
                    errors.append("bounding_box必须是包含4个整数的数组")
                elif not all(isinstance(x, int) for x in bbox):
                    errors.append("bounding_box中的所有值必须是整数")

        # 检查state_info子字段
        if "state_info" in json_data:
            state_info = json_data["state_info"]
            required_state_fields = ["is_enabled", "is_visible"]

            for field in required_state_fields:
                if field not in state_info:
                    errors.append(f"state_info缺少必需字段: {field}")

        # 检查action_info子字段
        if "action_info" in json_data:
            action_info = json_data["action_info"]
            if "default_action" not in action_info:
                errors.append("action_info缺少必需字段: default_action")

        # 检查metadata子字段
        if "metadata" in json_data:
            metadata = json_data["metadata"]
            required_metadata_fields = ["software_version", "author", "created_at", "updated_at"]

            for field in required_metadata_fields:
                if field not in metadata:
                    errors.append(f"metadata缺少必需字段: {field}")

        return len(errors) == 0, errors

    def update_existing_json(self, json_path, updated_data):
        """
        更新现有的JSON文件

        Args:
            json_path (str): JSON文件路径
            updated_data (dict): 更新的数据

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # 读取现有JSON文件
            with open(json_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            # 更新数据
            existing_data.update(updated_data)

            # 更新时间戳
            existing_data["metadata"]["updated_at"] = datetime.now().isoformat()

            # 保存更新后的文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

            return True, f"JSON文件已更新: {json_path}"

        except Exception as e:
            logging.error(f"更新JSON文件失败: {e}")
            return False, str(e)