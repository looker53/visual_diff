"""
TODO: 没有必要存储所有的图片，占空间太大了。只需存储baseline 和本轮图片。
"""

import hashlib
import yaml
from pathlib import Path
from selenium.webdriver.remote.webdriver import WebDriver


class Eye:
    def __init__(self, temp_dir=Path('./eye')):
        """初始化视觉查看器"""
        temp_dir.mkdir(parents=True, exist_ok=True)

        # 记录目前是第几次 build
        config_path = temp_dir / 'eye.yaml'
        if not config_path.exists():
            config_path.write_text('')
        try:
            current_build = read_yaml_option(config_path, 'current_build')
        except ValueError:
            current_build = 1
            new_yaml_option(config_path, 'current_build', current_build)
        else:
            if current_build is None:
                new_yaml_option(config_path, 'current_build', 1)
            else:
                current_build = update_yaml_option(config_path, 'current_build', current_build + 1)

        # 生成 build 文件夹，存储每次 build 截图
        build_dir = temp_dir / f"build-{current_build}"
        build_dir.mkdir(parents=True, exist_ok=True)

        self.build_dir = build_dir
        self.config_path = config_path

    def check_page(self, driver, threshold=1):
        """页面 diff"""
        # 页面 hash, 不 hash 直接存 url可能会异常
        page_reference = hash(driver.current_url)
        # 截图
        img = screenshot(driver)
        img_path = self.build_dir / f'{page_reference}.png'
        # 保存截图到此轮构建目录
        img_path = save_screenshot(img, img_path)
        # 获取截图的baseline
        baseline_path = self.get_baseline(page_reference)
        if not baseline_path:
            return self.set_baseline(page_reference, img_path)
        with open(baseline_path, 'rb') as f:
            baseline = f.read()
        # 截图和 baseline 校验
        diff_result = diff(img, baseline, threshold=threshold)
        if diff_result != 1:
            self.set_baseline(page_reference, img_path)
            error_msg = f"""\
            diff score: {diff_result}
            baseline_img: {baseline_path}
            build_img: {img_path}
            """
            raise AssertionError(error_msg)
        return diff_result

    def set_baseline(self, page_reference, img_path):
        """设置baseline"""
        update_yaml_option(self.config_path, page_reference, str(img_path))

    def get_baseline(self, page_reference):
        """获取baseline"""
        return read_yaml_option(self.config_path, page_reference)


def hash(url):
    """生成页面标识"""
    hash = hashlib.md5(url.encode())
    return hash.hexdigest()


def screenshot(driver: WebDriver) -> "Image":
    """截图"""
    return driver.get_screenshot_as_png()


def save_screenshot(img, img_path) -> "Path":
    """保存截图"""
    with open(img_path, 'wb') as f:
        f.write(img)
    return img_path


def diff(img1, img2, threshold=1):
    """图像对比"""
    if img1 != img2:
        return 0
    return 1


def update_yaml_option(fspath, option, value):
    """更新yaml选项"""
    stream = open(fspath, encoding='utf-8')
    options = yaml.safe_load(stream)
    if options is None:
        options = dict()
    options[option] = value
    with open(fspath, 'w', encoding='utf-8') as f:
        f.write(yaml.safe_dump(options))
    return value


def read_yaml_option(fspath, option):
    """读取yaml选项"""
    stream = open(fspath, encoding='utf-8')
    options = yaml.safe_load(stream)
    if options is None:
        raise ValueError('没有选项')
    return options.get(option)


def new_yaml_option(fspath, option, value):
    """创建yaml选项"""
    stream = open(fspath, encoding='utf-8')
    options = yaml.safe_load(stream)
    if options is None:
        options = dict()
    if options.get('option') is None:
        options[option] = value
    with open(fspath, 'w', encoding='utf-8') as f:
        f.write(yaml.safe_dump(options))
    return value


if __name__ == '__main__':
    print(hash('http://www.baidu.com'))
