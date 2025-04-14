import os
import requests
import argparse
import json
import sys
import locale
import traceback  # 添加traceback模块用于打印详细错误信息
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 不使用webdriver-manager自动下载
# from webdriver_manager.chrome import ChromeDriverManager

# 设置控制台输出编码
def set_console_encoding():
    """设置控制台编码，解决中文显示问题"""
    # 检测当前系统编码
    system_encoding = locale.getpreferredencoding()
    print(f"系统编码: {system_encoding}")
    
    # 设置stdout的编码
    if sys.stdout.encoding != 'utf-8':
        try:
            # 尝试设置为UTF-8
            sys.stdout.reconfigure(encoding='utf-8')
            print("已将控制台输出编码设置为UTF-8")
        except AttributeError:
            # Python 3.6或更早版本不支持reconfigure
            print("无法自动设置控制台编码，请手动设置命令行为UTF-8编码")
            print("可以在运行脚本前执行: chcp 65001")

class WechatImageDownloader:
    def __init__(self, output_dir='./wechat_images', min_width=200, min_height=200, 
                 wait_time=10, quality_filter=True, headless=False, driver_path=None):
        self.output_dir = output_dir
        self.min_width = min_width
        self.min_height = min_height
        self.wait_time = wait_time
        self.quality_filter = quality_filter
        self.headless = headless
        self.driver_path = driver_path  # 新增参数，用于手动指定chromedriver路径
        self.create_output_dir()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def create_output_dir(self):
        """创建输出目录"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建目录: {self.output_dir}")
            
    def init_driver(self):
        """初始化Selenium WebDriver"""
        print("初始化Chrome WebDriver...")
        
        # 检查chromedriver是否存在
        if self.driver_path and not os.path.exists(self.driver_path):
            print(f"错误：找不到ChromeDriver文件: {self.driver_path}")
            print("请确保您提供的路径正确，并且文件存在。")
            raise FileNotFoundError(f"找不到ChromeDriver文件: {self.driver_path}")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # 添加更多Chrome选项以提高稳定性
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
        
        # 添加中文支持
        chrome_options.add_argument('--lang=zh-CN')
        
        # 禁用图片加载以加快速度（我们只需要图片URL）
        chrome_options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )
        
        # 记录驱动版本检查点
        print("正在检查Chrome和ChromeDriver版本兼容性...")
        
        try:
            # 尝试使用直接创建driver的方式
            if self.driver_path:
                print(f"使用指定的ChromeDriver路径: {self.driver_path}")
                service = Service(executable_path=self.driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # 如果未指定路径，则使用默认方式
                print("使用默认方式创建Chrome WebDriver")
                driver = webdriver.Chrome(options=chrome_options)
            
            # 检查是否创建成功
            print("Chrome WebDriver初始化成功！")
            
            # 设置页面加载超时
            driver.set_page_load_timeout(30)
            
            return driver
            
        except Exception as e:
            print("\n====== 创建WebDriver失败 ======")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")
            print("\n详细错误堆栈:")
            traceback.print_exc()
            
            print("\n请尝试以下解决方案：")
            print("1. 手动下载与您Chrome浏览器版本匹配的ChromeDriver")
            print("   下载地址: https://chromedriver.chromium.org/downloads")
            print("2. 将下载的chromedriver.exe放在脚本同目录下")
            print("3. 使用 --driver-path 参数指定ChromeDriver路径")
            print("   例如: python getWechatImgs.py URL --driver-path=./chromedriver.exe")
            print("\n其他可能的解决方法:")
            print("- 尝试重启电脑后再运行")
            print("- 检查是否有其他程序占用了ChromeDriver")
            print("- 检查您的防病毒软件是否阻止了ChromeDriver的运行")
            print("- 确认您的Chrome浏览器可以正常启动")
            
            # 重新抛出异常以中止程序
            raise
    
    def wait_for_user_verification(self, driver):
        """等待用户完成验证"""
        print("\n============= 需要人工验证 =============")
        print("请在打开的浏览器窗口中完成验证...")
        input("完成验证后按回车键继续...")
        print("继续执行程序...\n")
    
    def process_wechat_article(self, url):
        """处理微信公众号文章，提取所有图片"""
        print(f"正在处理微信文章: {url}")
        
        driver = None
        try:
            # 尝试初始化WebDriver
            driver = self.init_driver()
            
            # 设置更长的页面加载超时
            try:
                print(f"正在加载页面: {url}")
                driver.get(url)
                print("页面加载成功")
            except Exception as e:
                print(f"页面加载失败: {str(e)}")
                print("尝试刷新页面...")
                driver.refresh()
            
            # 检查是否需要验证
            print("检查是否需要验证...")
            if not self.headless and ("验证" in driver.title or "请完成安全验证" in driver.page_source):
                self.wait_for_user_verification(driver)
            
            # 等待页面加载完成
            print(f"等待页面元素加载，最多等待 {self.wait_time} 秒...")
            try:
                WebDriverWait(driver, self.wait_time).until(
                    EC.presence_of_element_located((By.TAG_NAME, "img"))
                )
                print("页面元素加载完成")
            except Exception as e:
                print(f"等待页面元素超时: {str(e)}")
                print("继续执行，但可能影响图片提取效果")
            
            # 滚动页面以加载所有图片
            self.scroll_page(driver)
            
            # 获取页面内容
            print("获取页面内容...")
            html_content = driver.page_source
            
            # 解析页面
            print("解析HTML内容...")
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 提取文章标题用于文件夹命名
            print("提取文章标题...")
            title = self.get_article_title(soup)
            if title:
                # 使用安全的文件名
                safe_title = self.sanitize_filename(title)
                article_dir = os.path.join(self.output_dir, safe_title)
                if not os.path.exists(article_dir):
                    os.makedirs(article_dir)
                    print(f"创建文章目录: {article_dir}")
            else:
                article_dir = self.output_dir
                print(f"未找到文章标题，使用默认目录: {article_dir}")
                
            print(f"文章标题: {title}")
            print(f"保存目录: {article_dir}")
            
            # 寻找所有图片
            print("查找图片标签...")
            img_tags = soup.find_all('img')
            print(f"发现 {len(img_tags)} 个图片标签")
            
            if len(img_tags) == 0:
                print("警告：未找到图片标签，可能是页面结构不符合预期")
                print("正在保存页面源代码以便调试...")
                debug_file = os.path.join(self.output_dir, "debug_page.html")
                with open(debug_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"页面源代码已保存至: {debug_file}")
            
            # 提取并处理所有图片URL
            print("提取图片URL...")
            img_urls = []
            for img in img_tags:
                # 尝试不同的属性来获取微信图片URL
                img_url = None
                for attr in ['data-src', 'src', 'data-url', 'data-original']:
                    if img.get(attr):
                        url = img.get(attr)
                        # 微信图片URL通常以https://mmbiz开头
                        if url.startswith('https://mmbiz') or self.is_valid_image_url(url):
                            img_url = url
                            break
                
                if img_url:
                    # 对于微信图片，处理URL参数
                    img_url = self.process_wechat_img_url(img_url)
                    
                    # 检查图片尺寸信息
                    width = img.get('data-w') or img.get('width')
                    height = img.get('data-h') or img.get('height')
                    
                    if self.quality_filter and width and height:
                        try:
                            w, h = int(width), int(height)
                            if w < self.min_width or h < self.min_height:
                                continue
                        except ValueError:
                            pass
                    
                    img_urls.append(img_url)
            
            if not img_urls:
                print("未找到有效图片URL，请检查页面结构或验证是否完成")
                return 0
                
            print(f"找到 {len(img_urls)} 个有效图片URL")
            
            # 下载所有图片
            print("开始下载图片...")
            success_count = 0
            for i, img_url in enumerate(img_urls):
                try:
                    filename = f"image_{i+1}_{int(time.time())}_{random.randint(1000, 9999)}.jpg"
                    file_path = os.path.join(article_dir, filename)
                    
                    if self.download_image(img_url, file_path):
                        success_count += 1
                        print(f"[{success_count}/{len(img_urls)}] 已下载: {filename}")
                    
                    # 添加延迟
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    print(f"处理图片 {img_url} 时出错: {str(e)}")
            
            print(f"\n共成功下载 {success_count} 张图片到 {article_dir}")
            
            # 保存图片URL列表供参考
            urls_file = os.path.join(article_dir, "image_urls.txt")
            with open(urls_file, "w", encoding="utf-8") as f:
                for i, url in enumerate(img_urls):
                    f.write(f"图片 {i+1}: {url}\n")
            
            print(f"图片URL列表已保存至: {urls_file}")
            
            return success_count
            
        except Exception as e:
            print(f"处理页面时出错: {str(e)}")
            print("详细错误信息:")
            traceback.print_exc()
            return 0
        finally:
            if driver:
                try:
                    print("关闭Chrome WebDriver...")
                    driver.quit()
                    print("Chrome WebDriver已关闭")
                except Exception as e:
                    print(f"关闭WebDriver时出错: {str(e)}")
    
    def scroll_page(self, driver):
        """滚动页面以加载所有图片"""
        print("滚动页面以加载所有内容...")
        
        try:
            # 获取初始页面高度
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # 滚动到页面底部
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # 等待新内容加载
                time.sleep(2)
                
                # 计算新的页面高度
                new_height = driver.execute_script("return document.body.scrollHeight")
                
                # 如果页面高度没有变化，说明已经到底部了
                if new_height == last_height:
                    break
                    
                last_height = new_height
                
            # 回到顶部，再慢慢滚动一次以确保加载所有图片
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 慢慢滚动
            height = driver.execute_script("return document.body.scrollHeight")
            for i in range(10):
                driver.execute_script(f"window.scrollTo(0, {height * i / 10});")
                time.sleep(0.5)
                
            print("页面滚动完成")
            
        except Exception as e:
            print(f"滚动页面时出错: {str(e)}")
            print("继续执行，但可能影响图片提取效果")
    
    def get_article_title(self, soup):
        """获取微信文章标题"""
        # 尝试从不同元素获取标题
        title_selectors = [
            "h1#activity-name",
            "h2.rich_media_title",
            ".rich_media_title"
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if title:
                    return title
        
        return f"wechat_article_{int(time.time())}"
    
    def is_valid_image_url(self, url):
        """检查URL是否为有效的图片链接"""
        if not url.startswith(('http://', 'https://')):
            return False
            
        # 检查URL是否指向图片
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        if any(path.endswith(ext) for ext in image_extensions):
            return True
            
        # 微信的图片URL可能没有扩展名但包含某些关键字
        wechat_patterns = ['mmbiz', 'wx_fmt', 'wxfrom']
        return any(pattern in url.lower() for pattern in wechat_patterns)
    
    def process_wechat_img_url(self, url):
        """处理微信图片URL，获取高质量版本"""
        # 对于微信图片，尝试移除一些限制图片质量的参数
        if 'mmbiz' in url:
            # 移除缩放参数
            url = re.sub(r'&tp=webp&wxfrom=5.*?(&|$)', '&tp=png&wxfrom=5&wx_lazy=1', url)
            
            # 添加清晰度参数
            if 'wx_fmt=' not in url:
                url += '&wx_fmt=png'
        
        return url
    
    def download_image(self, url, file_path):
        """下载图片到指定路径"""
        try:
            response = requests.get(url, headers=self.headers, stream=True, timeout=15)
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                print(f"跳过非图片内容: {content_type}")
                return False
            
            # 写入文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 验证文件大小
            file_size = os.path.getsize(file_path)
            if file_size < 1024:  # 小于1KB的文件可能是错误的
                print(f"警告: 图片文件过小 ({file_size} 字节)，可能下载不完整")
            
            return True
            
        except Exception as e:
            print(f"下载图片失败 {url}: {str(e)}")
            return False
    
    def sanitize_filename(self, filename):
        """净化文件名，移除不合法字符"""
        # 移除不允许作为文件名的字符
        illegal_chars = r'[\\/*?:"<>|]'
        sanitized = re.sub(illegal_chars, '_', filename)
        
        # 限制长度
        if len(sanitized) > 50:
            sanitized = sanitized[:47] + '...'
            
        return sanitized


def main():
    # 设置控制台编码
    set_console_encoding()
    
    parser = argparse.ArgumentParser(description='从微信公众号文章批量下载图片')
    parser.add_argument('url', help='微信公众号文章URL')
    parser.add_argument('-o', '--output', default='./wechat_images', help='图片保存目录')
    parser.add_argument('-m', '--min-size', type=int, default=200, help='最小图片尺寸(宽或高，像素)')
    parser.add_argument('-w', '--wait', type=int, default=10, help='等待页面加载的最长时间(秒)')
    parser.add_argument('--no-filter', action='store_true', help='不过滤小图片和图标')
    parser.add_argument('--headless', action='store_true', help='使用无头模式(不显示浏览器)')
    parser.add_argument('--driver-path', help='指定Chrome驱动程序路径')
    
    args = parser.parse_args()
    
    # 显示脚本运行信息
    print("=" * 50)
    print(f"微信公众号图片批量下载工具 v1.1")
    print(f"下载目标: {args.url}")
    print(f"输出目录: {args.output}")
    print(f"最小图片尺寸: {args.min_size}px")
    print(f"ChromeDriver路径: {args.driver_path if args.driver_path else '默认'}")
    print("=" * 50)
    print()
    
    try:
        downloader = WechatImageDownloader(
            output_dir=args.output,
            min_width=args.min_size,
            min_height=args.min_size,
            wait_time=args.wait,
            quality_filter=not args.no_filter,
            headless=args.headless,
            driver_path=args.driver_path
        )
        
        downloader.process_wechat_article(args.url)
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序执行出错: {str(e)}")
        print("详细错误信息:")
        traceback.print_exc()
    
    print("\n程序执行完成")


if __name__ == "__main__":
    main() 