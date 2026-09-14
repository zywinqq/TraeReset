import os

# dmgbuild 配置 - 用于 GitHub Actions macOS 打包
# 生成 TraeReset-<version>.dmg

# DMG 卷名
volume_name = "TraeReset"

# DMG 输出格式
format = "UDBZ"  # bzip2 压缩

# 文件系统
files = []

# 自动查找 PyInstaller 输出的 .app
# PyInstaller --windowed 在 dist/ 下生成 TraeReset.app
app_path = "dist/TraeReset.app"
if os.path.isdir(app_path):
    files = [(app_path, "TraeReset.app")]

# 拖拽安装：Applications 文件夹快捷方式
symlinks = {"Applications": "/Applications"}

# 默认窗口设置：iconview 布局
icon_locations = {
    "TraeReset.app": (140, 120),
    "Applications": (500, 120),
}

# 背景图片（可选，无则纯色）
background = None

# 窗口大小
window_rect = ((100, 100), (640, 380))

# 图标大小
icon_size = 80

# 文字大小
text_size = 16

# 许可协议（可选）
license = None

# 卷大小
size = None  # 自动

# 删除所有 .DS_Store
remove_ds_store = True
