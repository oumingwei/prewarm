import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import json
import csv
import os
import time
import stable_match as stable_match
import  prewarm as gurobi
import SOCK as sock
import greedy as greedy

def panit_rate():
    multiple_data = json.load(open(('multiple.json')))
    multiple = []
    for i in range(len(multiple_data['multiple'])):
        index = 'm' + str(i + 1)
        multiple.append((multiple_data['multiple'][index]))
    countA_gurobi = np.zeros(len(multiple))
    countB_Stable = np.zeros(len(multiple))
    countC_SOCK = np.zeros(len(multiple))
    countD_greedy = np.zeros(len(multiple))
    c = sock.prewarm()
    y = c.random_y()
    for i in range(len(multiple)):
        b = stable_match.prewarm()
        a = gurobi.prewarm()
        d = greedy.prewarm()

        for j in range(len(b.function_list)):
            b.function_list[j].request_rate = b.function_list[j].request_rate * multiple[i]

        countB_Stable[i] = b.Coalitional_Game()

        for j in range(len(a.function_list)):
            a.function_list[j].request_rate = a.function_list[j].request_rate * multiple[i]
        countA_gurobi[i] = a.gurobi_solution()
        # for j in range(len(c.function_list)):
        #     c.function_list[j].request_rate *= multiple[i]
        # countC_SOCK[i] = c.sock(y)
        for j in range(len(d.function_list)):
            d.function_list[j].request_rate *= multiple[i]
        countD_greedy[i] = d.Greedy()
    mpl.rc('font', size=19)
    plt.rc('font', family='Times New Roman')
    # plt.title('The influence of the add of CA on the cost')
    plt.ylabel('Start time')
    plt.xlabel('the multiple of request rate')
    #   plt.scatter(multiple, countA_adapter,s=20)
    #   plt.scatter(multiple, countB_adapter,s=20)
    plt.plot(multiple, countA_gurobi, color='b', linestyle='-.', linewidth=3, label='gurobi')
    plt.scatter(multiple, countA_gurobi, color='b', marker='v', s=50)

    # plt.plot(multiple, countC_SOCK, color='darksalmon', linestyle='--', linewidth=3, label='SOCK')
    # plt.scatter(multiple, countC_SOCK, color='darksalmon', marker='^', s=50)

    plt.plot(multiple, countB_Stable, color='r', linestyle=':', linewidth=3, label='Stable')
    plt.scatter(multiple, countB_Stable, color='r', marker='<', s=50)

    plt.plot(multiple, countD_greedy, color='g', linestyle=':', linewidth=3, label='greedy')
    plt.scatter(multiple, countD_greedy, color='g', marker='<', s=50)
    plt.legend(),
    plt.grid()
    # plt.xlim([-3, 3])
    plt.xlim([1, 1.8])

    fig = plt.gcf()
    fig.set_size_inches(9, 3.5)
    plt.savefig('rate.png', bbox_inches='tight')
    f = open('rate.csv', 'w', encoding='utf-8')
    csv_writer = csv.writer(f)
    for i in range(len(multiple)):
        csv_writer.writerow([multiple[i], countA_gurobi[i], countB_Stable[i], countC_SOCK[i], countD_greedy[i]])
    f.close()
if __name__=="__main__":
    # a=stable_match.prewarm()
    # print(a.Coalitional_Game())
    panit_rate()


