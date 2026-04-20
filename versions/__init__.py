# versions/__init__.py
# 微信版本注册表：映射版本标签 → 模块路径
# 每次微信更新需要适配时，复制最新版本文件并在此处新增一行（最新版本放最前面）
VERSIONS = {
    "微信 4.1.9.21": "versions.wechat_4_1_9_21",
    "微信 4.1.8.107": "versions.wechat_4_1_8_107",
}


def get_version_labels():
    """返回版本标签列表，用于GUI下拉框"""
    return list(VERSIONS.keys())


def get_default_version():
    """返回默认（最新）版本标签"""
    return next(iter(VERSIONS.keys()))
