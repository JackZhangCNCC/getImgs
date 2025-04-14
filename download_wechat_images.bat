@echo off
chcp 65001 > nul
title 微信公众号图片批量下载工具

color 0A

:menu
cls
echo ===================================================
echo            微信公众号图片批量下载工具
echo ===================================================
echo.

:input_url
set url=
set /p url="请输入微信公众号文章链接(输入q退出): "
if "%url%"=="q" goto end
if "%url%"=="Q" goto end
if "%url%"=="" goto input_url

echo.
:input_driver
set driver_path=
set /p driver_path="请输入ChromeDriver路径 (直接回车使用默认位置): "

echo.
echo 开始下载图片...
echo.

REM 捕获错误处理
if "%driver_path%"=="" (
    python getWechatImgs.py "%url%" 2> error.log
) else (
    python getWechatImgs.py "%url%" --driver-path="%driver_path%" 2> error.log
)

if errorlevel 1 (
    echo.
    echo 执行过程中发生错误，请检查ChromeDriver配置。
    echo 详细错误信息已保存到error.log文件中。
    echo.
)

echo.
set choice=
set /p choice="是否继续下载其他文章? (y/n): "
if /i "%choice%"=="y" goto menu
if /i "%choice%"=="Y" goto menu
if /i "%choice%"=="" goto menu

:end
echo.
echo 感谢使用，再见!
echo.
timeout /t 3 > nul 