import os
import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re

class ImageDownloader:
    def __init__(self, output_dir='./images'):
        self.output_dir = output_dir
        self.create_output_dir()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def create_output_dir(self):
        """创建输出目录"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建目录: {self.output_dir}")
    
    def download_image(self, img_url, filename=None):
        """下载单张图片"""
        try:
            response = requests.get(img_url, headers=self.headers, stream=True, timeout=10)
            response.raise_for_status()
            
            # 如果没有提供文件名，从URL中提取
            if not filename:
                parsed_url = urlparse(img_url)
                filename = os.path.basename(parsed_url.path)
                # 如果文件名为空或不包含扩展名，生成随机文件名
                if not filename or '.' not in filename:
                    filename = f"image_{int(time.time())}_{random.randint(1000, 9999)}.jpg"
            
            file_path = os.path.join(self.output_dir, filename)
            
            # 写入文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"已下载: {filename}")
            return True
            
        except Exception as e:
            print(f"下载失败 {img_url}: {str(e)}")
            return False
    
    def download_from_url(self, url, use_selenium=False):
        """从URL下载所有图片"""
        if use_selenium:
            html_content = self._get_html_with_selenium(url)
        else:
            html_content = self._get_html_with_requests(url)
        
        if not html_content:
            return False
        
        # 解析HTML内容
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 寻找所有图片标签
        img_tags = soup.find_all('img')
        
        if not img_tags:
            print("没有找到图片")
            return False
        
        print(f"找到 {len(img_tags)} 张图片")
        
        # 下载所有图片
        downloaded_count = 0
        for i, img in enumerate(img_tags):
            img_url = None
            
            # 尝试不同的属性来获取图片URL
            for attr in ['src', 'data-src', 'data-original', 'data-url']:
                if img.get(attr):
                    img_url = img.get(attr)
                    break
            
            if not img_url:
                continue
            
            # 处理相对URL
            if not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(url, img_url)
            
            # 排除小图标、占位符等
            if self._is_valid_image(img_url, img):
                # 生成文件名
                filename = f"image_{i+1}_{int(time.time())}_{random.randint(1000, 9999)}.jpg"
                
                # 尝试下载图片
                if self.download_image(img_url, filename):
                    downloaded_count += 1
                    # 添加小延迟以避免被封
                    time.sleep(0.5)
        
        print(f"共下载 {downloaded_count} 张图片")
        return True
    
    def _get_html_with_requests(self, url):
        """使用requests获取HTML内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"获取页面失败: {str(e)}")
            return None
    
    def _get_html_with_selenium(self, url):
        """使用Selenium获取HTML内容(处理动态加载和需要验证的页面)"""
        try:
            print("使用Selenium加载页面...")
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")

            # 创建浏览器实例
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(url)
            
            # 等待页面加载
            time.sleep(5)
            
            # 获取页面内容
            html_content = driver.page_source
            driver.quit()
            
            return html_content
        except Exception as e:
            print(f"Selenium加载页面失败: {str(e)}")
            return None
    
    def _is_valid_image(self, url, img_tag):
        """判断是否为有效图片（排除小图标、占位符等）"""
        # 排除常见的小图标和按钮
        if 'icon' in url.lower() or 'button' in url.lower() or 'logo' in url.lower() or 'avatar' in url.lower():
            return False
        
        # 检查图片尺寸属性
        width = img_tag.get('width')
        height = img_tag.get('height')
        
        # 如果尺寸太小，可能是图标
        if width and height:
            try:
                w, h = int(width), int(height)
                if w < 50 or h < 50:
                    return False
            except ValueError:
                pass
        
        return True

def main():
    parser = argparse.ArgumentParser(description='从网页批量下载图片')
    parser.add_argument('url', help='要下载图片的网页URL')
    parser.add_argument('-o', '--output', default='./images', help='图片保存目录')
    parser.add_argument('-s', '--selenium', action='store_true', help='使用Selenium加载页面(处理动态加载的内容)')
    
    args = parser.parse_args()
    
    downloader = ImageDownloader(output_dir=args.output)
    downloader.download_from_url(args.url, use_selenium=args.selenium)

if __name__ == "__main__":
    main() 