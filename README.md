<p align="center"><img src="https://s2.ax1x.com/2019/06/09/Vs2Vv6.png"><h1>Min! A1pha-G0</h1></p>

使用 MCTS 算法实现的集结棋 (Lines of Action)。

## 一、小组成员及分工

- 郭帅帅 3160104060 （棋盘环境对象 `board.py`、GUI `app.py`、其他测试引擎 `random.py`, `greedy.py`, `human.py`）
- 何洪良 3160103176 （MCTS 引擎 `mcts.py`, `mcts_engine.py`）

## 二、开发环境

- Python 3.7.3
- Linux 4.19 / Windows 10

依赖：

- `PyQt5==5.12.2`

## 三、实现的功能

- 精美图形界面
- 人机博弈
- 显示双方计算时间
- 通过命令行参数动态调整双方引擎，实现模块化

## 四、运行方法

### 1. 建立虚拟环境（可选）

```
$ python3 -m venv venv
$ source venv/bin/activate
```

### 2. 安装依赖

```
(venv)$ pip install PyQt5==5.12.2
```

### 3. 运行

显示帮助：

```
(venv)$ python src/app.py -h
usage: app.py [-h] [-a ENGINE_A] [-b ENGINE_B]

Mini Alpha-Go. Available engines: mcts, random, greedy, human

optional arguments:
  -h, --help            show this help message and exit
  -a ENGINE_A, --engine_a ENGINE_A
                        Engine for player a (black). Default: human.
  -b ENGINE_B, --engine_b ENGINE_B
                        Engine for player b (white). Default: human.
```

人机博弈：

```
(venv)$ python src/app.py
```

黑方使用贪婪，白方使用 MCTS：

```
(venv)$ python src/app.py -a greedy -b mcts
```

