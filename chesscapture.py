# -*- coding: utf-8 -*-
"""
@author 星辰
@date 2024年03月23日 15:59:58
@packageName 
@className chess_screenshot
@version 1.0.0
@describe 捕获屏幕
"""
import win32con
import win32gui
import win32ui


def capture(window_title="QQ新中国象棋", save_path="game_capture.bmp"):
    """
    捕获指定窗口的屏幕截图并保存为位图文件。

    参数：
    - window_title: 要捕获的窗口的标题，默认为"QQ新中国象棋"。
    - save_path: 保存屏幕截图的文件路径，默认为"game_capture.bmp"。

    注意：
    - 使用前请确保安装了 pywin32 库。
    """
    # 获取窗口句柄
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd == 0:
        print("未找到指定窗口。")
        return

    # 获取窗口位置和大小
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    # 创建设备上下文
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    # 创建位图对象
    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)

    # 选择位图对象到设备上下文
    save_dc.SelectObject(save_bitmap)

    # 将窗口内容复制到位图对象
    save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

    # 保存位图到文件
    save_bitmap.SaveBitmapFile(save_dc, save_path)

    # 清理资源
    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)
