import cv2
import os
import concurrent.futures

from chesscapture import capture

# 按钮文件名与棋子的映射关系
BUTTON_MAPPING = {
    "A.png": "A",
    "A_1.png": "a",
    "B.png": "B",
    "B_1.png": "b",
    "C.png": "C",
    "C_1.png": "c",
    "K.png": "K",
    "K_1.png": "k",
    "N.png": "N",
    "N_1.png": "n",
    "P.png": "P",
    "P_1.png": "p",
    "R.png": "R",
    "R_1.png": "r"
}


def match_button(segment, button_dir):
    """
    匹配按钮

    Args:
        segment (numpy.ndarray): 图像片段.
        button_dir (str): 包含按钮图像的目录.

    Returns:
        str or None: 匹配的按钮文件名或None（未找到匹配）.
    """
    best_match = None
    best_similarity = 0

    # 遍历按钮目录中的所有按钮图片
    for button_filename in os.listdir(button_dir):
        if button_filename.endswith(".png"):
            button_path = os.path.join(button_dir, button_filename)
            button_image = cv2.imread(button_path)

            # 模板匹配
            result = cv2.matchTemplate(segment, button_image, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            # 更新最佳匹配
            if max_val > best_similarity:
                best_similarity = max_val
                best_match = button_filename  # 保留文件名，不去除扩展名

    # 如果相似度大于99.9%，则返回匹配的按钮名
    if best_similarity > 0.999:
        return best_match
    else:
        return None


def process_segment(args):
    image, start_x, start_y, interval_x, interval_y, box_size, button_dir, y = args
    row_fen = ''
    empty_count = 0
    height, width, _ = image.shape
    for x in range(start_x, start_x + interval_x * 9, interval_x):
        if x + box_size <= width and y + box_size <= height:
            segment = image[y:y + box_size, x:x + box_size]
            matched_button = match_button(segment, button_dir)
            if matched_button:
                piece = BUTTON_MAPPING.get(matched_button)
                if empty_count > 0:
                    row_fen += str(empty_count)
                    empty_count = 0
                row_fen += piece
            else:
                empty_count += 1
    if empty_count > 0:
        row_fen += str(empty_count)
    return row_fen


def img2fen(image_path="game_capture.bmp",
            start_x=242,
            start_y=76,
            interval_x=57,
            interval_y=57,
            box_size=52,
            button_dir="images/buttons"):
    capture()
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    with concurrent.futures.ThreadPoolExecutor() as executor:
        args_list = [(image, start_x, start_y, interval_x, interval_y, box_size, button_dir, y)
                     for y in range(start_y, start_y + interval_y * 10, interval_y)]
        results = list(executor.map(process_segment, args_list))

    original_fen = '/'.join(results)
    fen = transform_fen(original_fen)
    if fen == '///////// w':
        print('游戏窗口已被关闭或者最小化')
        return None
    else:
        return fen


def transform_fen(str_fen):
    """
    转换FEN字符串

    Args:
        str_fen (str): 原始FEN字符串.

    Returns:
        str: 转换后的FEN字符串.
    """
    segments = str_fen.split('/')
    # 如果前三行包含大写K，则需要转换大小写
    if any('K' in segment for segment in segments[:3]):
        toggled_string = str_fen.swapcase()  # 切换大小写
        return toggled_string + " w"
    else:
        return str_fen + " w"


def check_turn(image_path='game_capture.bmp',
               template_path=('images/buttons/T.png', 'images/buttons/T_1.png'),
               roi_coordinates=(143, 466, 212, 520)):
    capture()
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 初始化匹配结果列表
    results = []

    # 获取模板并进行模板匹配
    for tp in template_path:
        template = cv2.imread(tp)
        if template is None:
            print(f"模板读取失败'{tp}'")
            continue
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        x1, y1, x2, y2 = roi_coordinates
        roi = gray_image[y1:y2, x1:x2]
        try:
            result = cv2.matchTemplate(roi, gray_template, cv2.TM_CCOEFF_NORMED)
            results.append(result)
        except cv2.error:
            print("请勿要最小化游戏窗口")

    # 根据匹配结果进行逻辑判断
    threshold = 0.9
    for result in results:
        if result.max() > threshold:
            return True
    return False

