# Element Digitizer - UI元素数字化标注工具

## 概述

Element Digitizer 是一个专业的UI元素标注工具，旨在帮助数据标注人员高效、精准地从运行中的桌面应用程序中采集UI元素信息，并自动转换为结构化的JSON文件。

## 核心特性

- **全局热键激活**: 使用 `Ctrl+Shift+C` 快捷键随时启动屏幕捕获
- **可视化框选**: 通过拖拽鼠标绘制矩形框来精确选择UI元素
- **智能截图**: 自动截取选定区域并保存为高质量PNG图片
- **结构化标注**: 提供完整的表单界面来输入元素元数据
- **标准化输出**: 严格遵循UI Element Schema v1.0规范生成JSON文件
- **文件管理**: 自动组织文件到规范的目录结构中

## 系统要求

- Python 3.9 或更高版本
- Windows 10/11 (推荐) 或 Linux 桌面环境
- 至少 4GB RAM
- 100MB 可用磁盘空间

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone <https://github.com/Dece1ve-Zhang/Element-Digitizer.git>
cd element-digitizer
```

### 2. 创建虚拟环境 (推荐)

```bash
conda create -n DHDAS python=3.10

# Windows
conda activate DHDAS

```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 创建必要目录

程序会自动创建以下目录结构，但您也可以手动创建：

```
database/
├── ui_elements/
│   ├── screenshots/     # 存储截图文件
│   ├── default/         # 默认模块的JSON文件
│   └── [module_name]/   # 其他模块的JSON文件
```

## 使用方法

### 启动程序

```bash
python main.py
```

程序启动后会最小化到系统托盘，显示为一个图标。

### 基本操作流程

#### 阶段一：屏幕捕获

1. **激活捕获模式**:
   - 按下 `Ctrl+Shift+C` 全局热键，或
   - 右键点击系统托盘图标选择"开始捕获"
2. **框选UI元素**:
   - 屏幕会出现半透明灰色覆盖层
   - 鼠标光标变为十字准线
   - 按住左键拖拽绘制红色矩形框选择目标UI元素
   - 释放鼠标左键完成选择
3. **取消操作**: 按 `ESC` 键可随时退出捕获模式

#### 阶段二：元数据标注

捕获完成后会自动弹出标注窗口，包含以下区域：

**左侧 - 截图预览区**:

- 显示刚刚捕获的UI元素截图
- 显示元素的屏幕坐标信息

**右侧 - 表单区域**:

1. **基本信息** (必填项用 * 标记):
   - 元素ID *: 唯一标识符，只能包含小写字母、数字和下划线
   - 元素名称: 人类可读的元素描述
   - 元素类型: 从预定义列表中选择 (button, input_field, etc.)
   - 父元素ID: 可选，指定父级元素的ID
   - 模块名称: 用于文件目录分类，默认为 "default"
2. **位置信息**:
   - 锚点ID: 可选，用于定位的参考元素ID
3. **状态信息**:
   - 元素已启用: 复选框，默认勾选
   - 元素可见: 复选框，默认勾选
   - 工具提示: 鼠标悬停时显示的提示文本
4. **动作信息**:
   - 默认动作 *: 从预定义列表中选择 (click, input_text, etc.)
   - 预期结果描述: 执行动作后的预期结果
5. **元数据信息**:
   - 软件版本 *: 被测试软件的版本号
   - 作者 *: 标注人员姓名

#### 阶段三：保存文件

1. 填写完所有必要信息后，点击 **"生成并保存JSON"** 按钮
2. 程序会自动：
   - 验证表单数据的完整性和格式
   - 保存截图到 `database/ui_elements/screenshots/{element_id}.png`
   - 生成符合Schema的JSON文件到 `database/ui_elements/{module_name}/{element_id}.json`
3. 显示保存成功消息
4. 清空表单，准备下一次标注

## 文件输出格式

### JSON文件结构

生成的JSON文件严格遵循UI Element Schema v1.0规范：

```json
{
  "schema_version": "1.0",
  "element_id": "main_menu_button",
  "element_name": "主菜单按钮",
  "element_type": "button",
  "parent_element_id": null,
  "location_info": {
    "screenshot_path": "database/ui_elements/screenshots/main_menu_button.png",
    "bounding_box": [100, 150, 200, 180],
    "anchor_id": "header_toolbar"
  },
  "state_info": {
    "is_enabled": true,
    "is_visible": true,
    "tooltip": "打开主菜单"
  },
  "action_info": {
    "default_action": "click",
    "expected_outcome_desc": "显示主菜单下拉列表"
  },
  "metadata": {
    "software_version": "v2.1.0",
    "author": "张三",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

### 目录结构

```
database/
├── ui_elements/
│   ├── screenshots/
│   │   ├── main_menu_button.png
│   │   ├── save_button.png
│   │   └── ...
│   ├── default/
│   │   ├── main_menu_button.json
│   │   ├── save_button.json
│   │   └── ...
│   └── toolbar/
│       ├── toolbar_button1.json
│       └── ...
```

## 高级功能

### 全局热键

- 程序支持在任何应用程序运行时通过 `Ctrl+Shift+C` 激活捕获模式
- 热键监听在后台运行，不会影响其他程序的使用

### 系统托盘

- 程序最小化到系统托盘，不占用任务栏空间
- 右键托盘图标可访问快速菜单
- 左键点击托盘图标直接启动捕获模式

### 数据验证

- 自动验证必填字段
- 检查元素ID格式规范
- 确保生成的JSON符合Schema规范

## 故障排除

### 常见问题

1. **热键不响应**:
   - 确认没有其他程序占用相同快捷键
   - 以管理员权限运行程序 (Windows)
   - 检查防病毒软件是否阻止了程序
2. **截图质量问题**:
   - 确认显示器缩放设置为100%
   - 避免在屏幕保护程序激活时使用
3. **文件保存失败**:
   - 检查程序所在目录的写入权限
   - 确认磁盘空间充足
   - 检查文件名是否包含非法字符
4. **JSON格式错误**:
   - 检查表单中是否有特殊字符
   - 确认所有必填字段都已填写

### 日志文件

程序会自动生成日志文件 `element_digitizer.log`，记录详细的运行信息和错误信息，可用于故障诊断。

## 开发信息

### 技术栈

- **GUI框架**: PyQt6
- **全局热键**: pynput
- **屏幕截图**: mss
- **图像处理**: Pillow
- **数据格式**: JSON

### 项目结构

```
element-digitizer/
├── main.py                 # 程序主入口
├── capture_module.py       # 屏幕捕获模块
├── annotation_gui.py       # 标注界面模块
├── json_generator.py       # JSON生成器模块
├── requirements.txt        # 依赖包列表
├── README.md              # 使用说明
└── element_digitizer.log  # 运行日志
```

## 许可证

此项目仅供DHDAS内部使用，版权所有。

## 支持

如遇问题或需要功能改进，请联系开发团队。