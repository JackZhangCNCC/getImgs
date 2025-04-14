# ChromeDriver 配置指南

为了使用 `getWechatImgs.py` 脚本下载微信公众号图片，您需要配置 ChromeDriver。

## 步骤 1: 检查 Chrome 浏览器版本

1. 打开 Chrome 浏览器
2. 点击右上角的三点菜单
3. 选择 `帮助` > `关于 Google Chrome`
4. 记下显示的版本号（例如：109.0.5414.120）

## 步骤 2: 下载对应版本的 ChromeDriver

1. 访问 ChromeDriver 官方下载页面: https://chromedriver.chromium.org/downloads
2. 选择与您的 Chrome 版本相匹配的 ChromeDriver 版本
   - 例如，如果您的 Chrome 是 109.x.xxxx.xx，则下载 ChromeDriver 109.x
3. 下载适用于 Windows 的 zip 文件 (chromedriver_win32.zip)

## 步骤 3: 解压并配置 ChromeDriver

1. 解压下载的 zip 文件，您将获得 `chromedriver.exe`
2. 您有两种配置方式:

### 方法 1: 将 ChromeDriver 放在脚本同目录下（推荐）

1. 将 `chromedriver.exe` 复制到与 `getWechatImgs.py` 相同的目录中
2. 运行 `download_wechat_images.bat` 时，无需额外指定路径

### 方法 2: 将 ChromeDriver 放在其他位置

1. 将 `chromedriver.exe` 放在您选择的任何位置
2. 运行 `download_wechat_images.bat` 时，输入完整的 ChromeDriver 路径
   - 例如: `C:\Tools\chromedriver.exe`

## 故障排除

如果遇到 `OSError: [WinError 193] %1 不是有效的 Win32 应用程序。` 错误，可能是以下原因：

1. **ChromeDriver 版本与 Chrome 不匹配**
   - 确保下载的 ChromeDriver 版本与您的 Chrome 浏览器版本匹配
   
2. **下载的文件不完整或损坏**
   - 重新下载 ChromeDriver
   
3. **32位/64位不匹配**
   - 如果您使用的是 64 位 Windows，尝试下载 chromedriver_win32.zip（仍然适用于 64 位系统）

4. **杀毒软件拦截**
   - 检查您的杀毒软件是否阻止了 ChromeDriver 的运行
   - 考虑将脚本目录添加到杀毒软件的排除列表中

## 更多资源

- ChromeDriver 官方文档: https://chromedriver.chromium.org/
- Chrome 版本历史: https://chromiumdash.appspot.com/releases?platform=Windows 