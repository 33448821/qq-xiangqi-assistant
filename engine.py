# -*- coding: utf-8 -*-
"""
@author 星辰
@date 2024年03月24日 11:29:12
@packageName 
@className command
@version 1.0.0
@describe 调用引擎思考部分
"""
import re
import subprocess


def run_chess_engine(movetime=5000, fen="rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w", engine_id=0):
    """
    运行运算引擎
    :param engine_id: 引擎id
    :param movetime: 思考计算时间
    :param fen:棋盘fen字符串
    :return:自己思考的走法和对方可能的走法
    """
    if engine_id == 0:
        engine_path = "engine/pikafish-bmi2.exe"
    elif engine_id == 1:
        engine_path = "engine/cyclone.exe"
    else:
        engine_path = "engine/cyclone.exe"

    if movetime <= 0:
        movetime = 1

    with subprocess.Popen(engine_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as engine_process:
        commands = [
            "position fen " + fen + "\n",
            "go movetime " + str(movetime) + "\n",
        ]

        for cmd in commands:
            engine_process.stdin.write(cmd)
            engine_process.stdin.flush()

        while True:
            output = engine_process.stdout.readline()
            if not output:
                break
            if "bestmove" in output:
                # 提取bestmove和ponder之间的字符串
                match = re.search(r'bestmove (.+?) ponder', output)
                if match:
                    bestmove = match.group(1).replace(" ", "")
                    # 提取ponder后面的字符串
                    match_ponder = re.search(r'ponder (.+)', output)
                    ponder = match_ponder.group(1).replace(" ", "")
                    engine_process.stdin.close()
                    engine_process.stdout.close()
                    return bestmove, ponder
                else:
                    bestmove = output.split()[1]
                    ponder = 'e0e9'
                    return bestmove, ponder
