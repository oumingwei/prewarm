#!/usr/bin/python3
# -*- coding:utf-8 -*-


#这个是sock真实实验跑出来的数据图，用以对比冷启动和prewarm
import copy

import matplotlib.pyplot as plt
import numpy as np




def plot_line(x_data, y_data, save_path, x_label, y_label,
              var_orient='vertical'):
    if var_orient != 'vertical' and var_orient != 'horizon':
        print('plot_figure var_orient error!')
        exit(1)
    if var_orient == 'vertical':
        y_data = list(map(list, zip(*y_data)))
    x_number = len(y_data[0])
    y_number = len(y_data)
    if len(x_data) != x_number:
        print('x_data和y_data不匹配！')
        exit(1)
    # 设置y_data的label、color、linestyle、marker
    # label = ['']
    # label = ['Normal copy mode',
    #          'Zero-copy mode']
    # label = ['Copy 1024 packets at a time',
    #          'Copy 2048 packets at a time']
    label = ['Serial PCIe', 'Parallel PCIe', 'Hybrid PCIe']
    # HTML颜色名 'red', 'green', 'blue', 'yellow', 'black', 'white',
    # 'cyan', 'darksalmon', 'gold', 'crimson'
    # color = ['red']
    # color = ['red', 'green']
    color = ['red', 'green', 'black']
    # 线条风格 '-', '--', '-.', ':', 'None'
    # linestyle = ['-']
    # linestyle = ['-', '--']
    linestyle = ['-', '--', '-.']
    # 线条标记 'o', 'd', 'D', 'h', 'H', '_', '8', 'p', ',', '.', 's',
    #  '+', '*', 'x', '^', 'v', '<', '>', '|'
    # marker = ['o']
    # marker = ['v', '^']
    marker = ['v', '^', 'o']
    if y_number != len(label) or y_number != len(color) or \
            y_number != len(linestyle) or y_number != len(marker):
        print('y_data的label、color、linestyle、marker没有被正确设置！')
        exit(1)
    # 设置字体和大小
    plt.rc('font', family='Times New Roman', size=15)
    # plt.title('title')
    # 设置x轴的标签
    plt.xlabel(x_label)
    # 设置x轴的范围
    # plt.xlim([0, 5])
    # 设置y轴的标签
    plt.ylabel(y_label)
    # 设置y轴的范围
    # plt.ylim([-5, 25])
    for _ in range(y_number):
        plt.plot(x_data, y_data[_], label=label[_],
                 color=color[_], linestyle=linestyle[_], linewidth=3)
        plt.scatter(x_data, y_data[_], color=color[_], marker=marker[_], s=50)
    # 'x' 'y' 'both'
    plt.grid(axis='y')
    plt.legend(loc=1)
    fig = plt.gcf()
    # 设置图片的长和宽（英寸）
    fig.set_size_inches(9, 3.5)
    if save_path is not None:
        plt.savefig(save_path, bbox_inches='tight')
        print('已将图像保存为'+save_path)
    plt.show()


def plot_bar(x_data, y_data, save_path, x_label, y_label,
             var_orient='vertical'):
    if var_orient != 'vertical' and var_orient != 'horizon':
        print('plot_figure var_orient error!')
        exit(1)
    if var_orient == 'vertical':
        y_data = list(map(list, zip(*y_data)))
    x_number = len(y_data[0])
    y_number = len(y_data)
    if len(x_data) != x_number:
        print('x_data和y_data不匹配！')
        exit(1)
    # 设置y_data的label、color、hatch
    label = ['pre-warm', 'cold start']
    # HTML颜色名 'red', 'green', 'blue', 'yellow', 'black', 'white', 'cyan',
    #  'darksalmon', 'gold', 'crimson'
    color = ['red', 'cornflowerblue']
    # 填充效果 '/', '|', '-', '+', 'x', 'o', 'O', '.', '*', ' '
    # hatch = ['x', '.']
    if y_number != len(label) or y_number != len(color):
        print('y_data的label、color、hatch没有被正确设置！')
        exit(1)
    # 设置字体和大小
    plt.rc('font', family='Times New Roman', size=15)
    # plt.title('title')
    # 设置柱状体的宽度
    bar_width = 0.4
    # 设置x轴的标签
    plt.xlabel(x_label)

    # 设置x轴的范围
    # plt.xlim([0, 21])
    # 设置x轴的刻度
    plt.xticks(np.arange(x_number)+bar_width*(y_number/2-0.5), x_data)
    # 设置y轴的标签
    plt.ylabel(y_label)
    # 设置y轴的范围
    # plt.ylim([-5, 25])
    for _ in range(y_number):
        plt.bar(np.arange(x_number)+_*bar_width,
                y_data[_], label=label[_], color=color[_],
                width=bar_width)
    # 'x' 'y' 'both'
    plt.grid(axis='y')
    plt.legend(loc=1)
    fig = plt.gcf()
    # 设置图片的长和宽（英寸）
    fig.set_size_inches(9, 3.5)
    if save_path is not None:
        plt.savefig(save_path, bbox_inches='tight')
        print('已将图像保存为'+save_path)
    print('若图像出现重叠现象，调小bar_width的值！')
    plt.show()


def plot_stacked_bar(x_data, y_data, save_path, x_label, y_label,
                     var_orient='vertical'):
    print('在堆叠柱状图中序号小的y_data位于柱状图下层')
    if var_orient != 'vertical' and var_orient != 'horizon':
        print('plot_figure var_orient error!')
        exit(1)
    if var_orient == 'vertical':
        y_data = list(map(list, zip(*y_data)))
    x_number = len(y_data[0])
    y_number = len(y_data)
    if len(x_data) != x_number:
        print('x_data和y_data不匹配！')
        exit(1)
    # 计算堆叠后的_y_data
    _y_data = copy.deepcopy(y_data)
    for i in range(y_number):
        for j in range(x_number):
            if i-1 >= 0:
                _y_data[i][j] += _y_data[i-1][j]
    # 百分比保留几位小数
    decimal = 2
    # 计算堆叠柱状图的百分比
    prop_y_data = copy.deepcopy(y_data)
    for i in range(y_number):
        for j in range(x_number):
            prop_y_data[i][j] = round(
                y_data[i][j]/_y_data[y_number-1][j], decimal)
    # 设置y_data的label、color、hatch
    label = ['label1', 'label2', 'label3']
    # HTML颜色名 'red', 'green', 'blue', 'yellow', 'black', 'white',
    # 'cyan', 'darksalmon', 'gold', 'crimson'
    color = ['green', 'red', 'darksalmon']
    # 填充效果 '/', '|', '-', '+', 'x', 'o', 'O', '.', '*', ' '
    hatch = [' ', ' ', ' ']
    if y_number != len(label) or y_number != len(color) or \
            y_number != len(hatch):
        print('y_data的label、color、hatch没有被正确设置！')
        exit(1)
    # 设置字体和大小
    plt.rc('font', family='Times New Roman', size=15)
    # plt.title('title')
    # 设置柱状体的宽度
    bar_width = 0.6
    # 设置x轴的标签
    plt.xlabel(x_label)
    # 设置x轴的范围
    # plt.xlim([0, 5])
    # 设置x轴的刻度
    plt.xticks(np.arange(x_number), x_data)
    # 设置y轴的标签
    plt.ylabel(y_label)
    # 设置y轴的范围
    plt.ylim([0, 65])
    for _ in range(y_number-1, - 1, - 1):
        plt.bar(np.arange(x_number),
                _y_data[_], label=label[_], color=color[_], hatch=hatch[_],
                width=bar_width)
    # 添加堆叠柱状图的百分比
    for i in range(y_number):
        for j in range(x_number):
            plt.text(j, _y_data[i][j]-y_data[i][j]/2, s=str(
                prop_y_data[i][j]), ha='center', va='center', fontsize=14)
    # 'x' 'y' 'both'
    plt.grid(axis='y')
    plt.legend(loc=1)
    fig = plt.gcf()
    # 设置图片的长和宽（英寸）
    fig.set_size_inches(9, 3.5)
    if save_path is not None:
        plt.savefig(save_path, bbox_inches='tight')
        print('已将图像保存为'+save_path)
    print('若图像出现重叠现象，调小bar_width的值！')
    plt.show()


def benchmark():
    # cd python;rm -rf __pycache__;cd ..;rm -rf data1.eps data2.eps data3.eps
    x_data = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,'AVG'
]
    y_data = [[0.589664221,
0.875875473,
0.025399446,
0.028973341,
0.027787447,
0.030967474,
0.474486113,
0.19000411,
0.027033806,
0.032186747,
0.029177904,
0.027634621,
0.033230066,
0.028226852,
0.027630091,
0.022236347,
0.02876997,
0.030561686,
0.03085947,
0.198569298,
0.137963724
],
              [0.98241663,
1.022445679,
0.780859947,
0.671422005,
0.904851675,
0.734202147,
0.922185421,
0.883951664,
0.708868742,
0.747999191,
0.870368481,
0.964450121,
0.759003639,
0.741555691,
0.787734509,
0.816328049,
0.762723684,
0.785484791,
0.823967457,
0.957074165,
0.831394684
]]
    plot_bar(x_data, y_data, 'data2.eps', 'Action number', 'Start time', 'horizon')


if __name__ == '__main__':
    benchmark()
