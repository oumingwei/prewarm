import json
import time

from gurobipy import *
from node import node
from function import function
from package import package
class prewarm:
    def __init__(self):
        self.node_list = []#N
        self.function_list = []#F
        self.package_list = []#P
        node_data = json.load(open('node.json'))
        for i in range(len(node_data["node"])):
            index = 'n' + str(i + 1)
            node1 = node(node_data["node"][index]["id"],
                         node_data["node"][index]["disk_R"],
                         node_data["node"][index]["memory_r"],
                         node_data["node"][index]["cpu_resources"],
                         node_data["node"][index]["Bn"])
            for j in range(len(node_data["node"][index]["Tc"])):
                index1 = 'f' + str(j + 1)
                node1.Tc.append(node_data["node"][index]["Tc"][index1])
            self.node_list.append(node1)

        function_data = json.load(open('function.json'))
        for i in range(len(function_data["function"])):
            index = 'f' + str(i + 1)
            fun = function(function_data["function"][index]["id"],
                           function_data["function"][index]["cpu_resource_need"],
                           function_data["function"][index]["request_rate"])
            for j in range(len(function_data["function"][index]["need_packages"])):
                index1 = 'p'+str(j+1)
                fun.need_packages.append(function_data["function"][index]["need_packages"][index1])
            self.function_list.append(fun)

        package_data = json.load(open('package.json'))
        for i in range(len(package_data["package"])):
            index = 'p' + str(i + 1)
            pac = package(package_data["package"][index]["id"], package_data["package"][index]["size"])
            for j in range(len(self.node_list)):
                index2 = 'n' + str(j)
                pac.download_time[j] = package_data["package"][index]["download_time"][index2]
                pac.import_time[j] = package_data["package"][index]["import_time"][index2]
            self.package_list.append(pac)

    def gurobi_solution(self):
        m = Model()
        # 添加变量y,function f 是否在节点n上
        y = [[0 for i in range(len(self.node_list))]for n in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            for n in range(len(self.node_list)):
                y[f][n] = m.addVar(vtype=GRB.BINARY, name="y" + str(f + 1) + str(n + 1))

        # 添加变量x，节点n的硬盘中是否有package p
        x = [[None for n in range(len(self.package_list))]for i in range(len(self.node_list))]
        for n in range(len(self.node_list)):
            for p in range(len(self.package_list)):
                x[n][p] = m.addVar(vtype=GRB.BINARY, name="x" + str(n + 1) + str(p + 1))

        # Initialize some constants
        # Rn Node n hard disk capacity
        # Pt Node n cpu resource
        # rn Memory capacity of node n
        # 初始化theta
        theta = [[0 for p in range(len(self.package_list))] for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            for p in self.function_list[f].need_packages:
                theta[f][p] = 1
        lambd = [0 for i in range(len(self.function_list))]
        for i in range(len(self.function_list)):
            lambd[i] = self.function_list[i].request_rate
        H = [0 for n in range(len(self.node_list))]
        Cn = [0 for n in range(len(self.node_list))]
        M = [0 for n in range(len(self.node_list))]
        Bn = [0 for n in range(len(self.node_list))]
        Tc = [[0 for f in range(len(self.function_list))] for i in range(len(self.node_list))]  # 拉取一个容器的时间
        for n in range(len(self.node_list)):
            H[n] = self.node_list[n].disk_R
            M[n] = self.node_list[n].memory_r
            Cn[n] = self.node_list[n].cpu_resources
            Bn[n] = self.node_list[n].Bn
            for f in range(len(self.function_list)):
                Tc[n][f] = self.node_list[n].Tc[f]
        # Cj Calculation resource size required by function j
        C = [0 for j in range(len(self.function_list))]
        for j in range(len(self.function_list)):
            C[j] = self.function_list[j].cpu_resource_need
        # 设置一些常量
        s = [0 for i in range(len(self.package_list))]
        TI = [[0 for n in range(len(self.node_list))] for i in range(len(self.package_list))]
        Td = [[0 for n in range(len(self.node_list))] for i in range(len(self.package_list))]
        for i in range(len(self.package_list)):
            s[i] = self.package_list[i].size
            for n in range(len(self.node_list)):

                TI[i][n] = self.package_list[i].import_time[n]
                Td[i][n] = self.package_list[i].download_time[n]
        # 添加硬盘大小的约束
        for n in range(len(self.node_list)):
            m.addConstr(sum(x[n][i] * s[i] for i in range(len(self.package_list))) <= H[n], name="1")
            m.addConstr(sum(y[f][n] * C[f] * lambd[f] for f in range(len(self.function_list))) <= Cn[n], name="2")

        Zn = [0 for i in range(len(self.node_list))]
        for n in range(len(self.node_list)):
            Zn[n] = int(self.node_list[n].memory_r/self.node_list[n].Bn)

        #添加zni变量，表示containeri 在不在n上
        z = [[None for i in range(Zn[n])]for n in range(len(self.node_list))]
        for n in range(len(self.node_list)):
            for i in range(Zn[n]):
                z[n][i] = m.addVar(vtype=GRB.BINARY, name="z" + str(n + 1) + str(i + 1))
        #添加变量gama,function f 是否使用了节点n上的容器 i
        gamma = [[[None for i in range(Zn[n])]for n in range(len(self.node_list))]for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            for n in range(len(self.node_list)):
                for i in range(Zn[n]):
                    gamma[f][n][i] = m.addVar(vtype=GRB.BINARY, name="gama"+str(f+1)+str(n+1)+str(i+1))

        #添加变量 alpha,表示节点n上的容器i是否导入了package p
        alpha = [[[None for p in range(len(self.package_list))]for i in range(Zn[n])]for n in range(len(self.node_list))]
        for n in range(len(self.node_list)):
            for i in range(Zn[n]):
                for p in range(len(self.package_list)):
                    alpha[n][i][p] = m.addVar(vtype=GRB.BINARY, name="alpha"+str(n+1)+str(i+1)+str(p+1))
        #添加约束3，4，5
        for f in range(len(self.function_list)):
            for n in range(len(self.node_list)):
                for i in range(Zn[n]):
                    m.addConstr(gamma[f][n][i] <= z[n][i], name="3")
        for n in range(len(self.node_list)):
            for i in range(Zn[n]):
                for p in range(len(self.package_list)):
                    m.addConstr(alpha[n][i][p] <= z[n][i], name="4")
                    m.addConstr(alpha[n][i][p] <= x[n][p], name="5")
        #添加约束6
        for n in range(len(self.node_list)):
            for f in range(len(self.function_list)):
                m.addConstr(sum(gamma[f][n][i]for i in range(Zn[n])) <= y[f][n], name="6")
        #添加约束7
        for n in range(len(self.node_list)):
            m.addConstr(sum(z[n][i]*(sum(alpha[n][i][p]*s[p]for p in range(len(self.package_list)))+Bn[n])for i in range(Zn[n])) <= M[n], name="7")



        #添加约束8
        for f in range(len(self.function_list)):
            for n in range(len(self.node_list)):
                for i in range(Zn[n]):
                    for p in range(len(self.package_list)):
                        m.addConstr(gamma[f][n][i] * alpha[n][i][p] <= theta[f][p], name="8")
        #添加约束9
        for f in range(len(self.function_list)):
            m.addConstr(sum(y[f][n]for n in range(len(self.node_list))) == 1, name="9")



        #线性化引入变量belta
        belta = [[[[None for p in range(len(self.package_list))]for i in range(Zn[n])]for n in range(len(self.node_list))]for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            for n in range(len(self.node_list)):
                for i in range(Zn[n]):
                    for p in range(len(self.package_list)):
                        belta[f][n][i][p] = m.addVar(vtype=GRB.BINARY, name="belta"+str(f+1)+str(n+1)+str(i+1)+str(p+1))

        # #对belta进行约束
        for f in range(len(self.function_list)):
            for n in range(len(self.node_list)):
                for i in range(Zn[n]):
                    for p in range(len(self.package_list)):
                        m.addConstr(belta[f][n][i][p] <= theta[f][p],name="belta1")
                        m.addConstr(belta[f][n][i][p] <= y[f][n],name="belta2")
                        m.addConstr(belta[f][n][i][p] <= gamma[f][n][i],name="belta3")
                        m.addConstr(belta[f][n][i][p] <= alpha[n][i][p],name="belta4")
        g = [[None for n in range(len(self.node_list))]for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            for n in range(len(self.node_list)):
                g[f][n] = sum(gamma[f][n][i]for i in range(Zn[n]))
        tp = [None for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            tp[f] = sum((1-g[f][n])*y[f][n]*Tc[n][f] for n in range(len(self.node_list)))

        td = [None for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            td[f] = sum(theta[f][p]*(1-x[n][p])*Td[p][n]*g[f][n]
                        for n in range(len(self.node_list))
                        for p in range(len(self.package_list)))

        ti = [None for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            ti[f] = sum(theta[f][p]*y[f][n]*TI[p][n]*(gamma[f][n][i]-belta[f][n][i][p])
                   for n in range(len(self.node_list))
                   for p in range(len(self.package_list))
                   for i in range(Zn[n]))

        m.setObjective(sum(lambd[f]*(tp[f] + td[f]+ti[f]) for f in range(len(self.function_list))), GRB.MINIMIZE)
        t_start = time.time()
        m.optimize()
        t_end = time.time()

        print(y[4][3].x)
        for v in m.getVars():
                print('%s %g' % (v.varName, v.x))
        print('obj:%g' % m.objval)
        return m.objval



if __name__ == '__main__':
    a = prewarm()
    a.gurobi_solution()
