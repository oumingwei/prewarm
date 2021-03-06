import json
import random
import time
from copy import copy


from Container import Container
from node import node
from function import function
from package import package
class prewarm:
    def __init__(self):
        self.node_list = []  # N
        self.function_list = []  # F
        self.package_list = []  # P
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
                index1 = 'p' + str(j + 1)
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

        self.memory = [0 for n in range(len(self.node_list))]
        self.Disk = [0 for n in range(len(self.node_list))]
        self.cpu = [0 for n in range(len(self.node_list))]
        for n in range(len(self.node_list)):
            self.memory[n] = self.node_list[n].memory_r
            self.Disk[n] = self.node_list[n].disk_R
            self.cpu[n]= self.node_list[n].cpu_resources


    def greedy_y(self):
        for f in self.function_list:
            f.similarity.clear()
        for n in self.node_list:
            n.functions.clear()
            n.cpu_resources = self.cpu[n.node_id]
        for f in self.function_list:
            for f2 in self.function_list:
                if f != f2:
                    f.similarity[f2.id] = len(set(f.need_packages).intersection(set(f2.need_packages)))
        for f in self.function_list:
            Most_suitable_node = [-999, 0]
            for n in self.node_list:
                if n.cpu_resources >= f.cpu_resource_need * f.request_rate:
                    for _ in n.functions:
                        if Most_suitable_node[1] < f.similarity[_.id]:
                            Most_suitable_node = [n.node_id, f.similarity[_.id]]
            if Most_suitable_node[1] > 0:
                self.node_list[Most_suitable_node[0]].functions.append(f)
                self.node_list[Most_suitable_node[0]].cpu_resources -= f.cpu_resource_need * f.request_rate
            else:
                Most_memory_node =[]
                for n in self.node_list:
                    Most_memory_node.append([n, n.memory_r])
                Most_memory_node.sort(key=lambda x: x[1], reverse=True)
                for n in Most_memory_node:
                    if n[0].cpu_resources >= f.cpu_resource_need * f.request_rate:
                        n[0].functions.append(f)
                        n[0].cpu_resources -= f.cpu_resource_need * f.request_rate
                        break
        return self.gener_y()

    def zygote_generation(self, y):
        # ???????????????????????????stable match???????????????????????????????????????package?????????
        # 1.??????????????????????????????
        Zn = [0 for i in range(len(self.node_list))]
        for n in range(len(self.node_list)):
            Zn[n] = int(self.memory[n]/ self.node_list[n].Bn)
        z = [[0 for i in range(Zn[n])] for n in range(len(self.node_list))]
        gamma = [[[0 for i in range(Zn[n])] for n in range(len(self.node_list))] for f in
                 range(len(self.function_list))]
        alpha = [[[0 for p in range(len(self.package_list))] for i in range(Zn[n])] for n in
                 range(len(self.node_list))]
        x = [[0 for p in range(len(self.package_list))]for n in range(len(self.node_list))]

        Container_pool=[[]for n in range(len(self.node_list))]# ??????????????????????????????
        for n in range(len(self.node_list)):
            Container_pool[n] = copy(self.zygote_generation_n(y, n))# ??????????????????zygote????????????
        #????????????????????????????????????
        for n in range(len(self.node_list)):
            for i in Container_pool[n]:
                for f in i.functions:
                    gamma[f.id][n][i.id] = 1
                for p in i.packages:
                    alpha[n][i.id][p.id] = 1
                z[n][i.id] = 1
            for pl in self.node_list[n].packages:
                x[n][pl.id] = 1
      # ?????????????????????
        return self.caculate_result(y, x, gamma, alpha, Zn), x, gamma, alpha, z, Zn
    def show(self,y, x, gama, alpha, z, Zn, result):
        for n in range(len(self.node_list)):
            for p in range(len(self.package_list)):
                if x[n][p] == 1:
                    print("x" + str(n + 1) + str(p + 1) + "=1")
        for f in range(len(self.function_list)):
            for n in range(len(self.node_list)):
                if y[f][n] == 1:
                    print("y" + str(f + 1) + str(n + 1) + "=1")
        for f in range(len(self.function_list)):
            for n in range(len(self.node_list)):
                for i in range(Zn[n]):
                    if gama[f][n][i] == 1:
                        print("gama" + str(f + 1) + str(n + 1) + str(i + 1) + "=1")

        for n in range(len(self.node_list)):
            for i in range(Zn[n]):
                for p in range(len(self.package_list)):
                    if alpha[n][i][p] == 1:
                        print("alpha" + str(n + 1) + str(i + 1) + str(p + 1) + "=1")

        for n in range(len(self.node_list)):
            for i in range(Zn[n]):
                if z[n][i] == 1:
                    print("z" + str(n + 1) + str(i + 1) + "=1")
        print(result)

    def caculate_result(self, y, x, gama, alpha, Zn):
        theta = [[0 for p in range(len(self.package_list))] for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            for p in self.function_list[f].need_packages:
                theta[f][p] = 1
        lambd = [0 for i in range(len(self.function_list))]
        for i in range(len(self.function_list)):
            lambd[i] = self.function_list[i].request_rate

        H = [0 for n in range(len(self.node_list))]  # ????????????
        Cn = [0 for n in range(len(self.node_list))]  # cpu??????
        M = [0 for n in range(len(self.node_list))]  # ????????????
        Bn = [0 for n in range(len(self.node_list))]  # ????????????????????????????????????
        Tc = [[0 for f in range(len(self.function_list))] for i in range(len(self.node_list))] # ???????????????????????????
        for n in range(len(self.node_list)):
            H[n] = self.node_list[n].disk_R
            M[n] = self.node_list[n].memory_r
            Cn[n] = self.node_list[n].cpu_resources
            Bn[n] = self.node_list[n].Bn
            for f in range(len(self.function_list)):
                Tc[n][f] = self.node_list[n].Tc[f]
        # Cj Calculation resource size required by function j
        C = [0 for j in range(len(self.function_list))]  # function?????????CPU??????
        for j in range(len(self.function_list)):
            C[j] = self.function_list[j].cpu_resource_need
        TI = [[0 for n in range(len(self.node_list))] for i in range(len(self.package_list))]
        Td = [[0 for n in range(len(self.node_list))] for i in range(len(self.package_list))]
        for i in range(len(self.package_list)):
            for n in range(len(self.node_list)):
                TI[i][n] = self.package_list[i].import_time[n]
                Td[i][n] = self.package_list[i].download_time[n]

        g = [[0 for n in range(len(self.node_list))] for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            for n in range(len(self.node_list)):
                g[f][n] = sum(gama[f][n][i] for i in range(Zn[n]))
        tp = [0 for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            tp[f] = sum((1 - g[f][n]) * y[f][n] * Tc[n][f] for n in range(len(self.node_list)))

        td = [0 for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            td[f] = sum(y[f][n] * theta[f][p] * (1 - x[n][p]) * Td[p][n]*g[f][n]
                        for n in range(len(self.node_list))
                        for p in range(len(self.package_list)))
        ti = [0 for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            ti[f] = sum(theta[f][p] * y[f][n] * TI[p][n] * (gama[f][n][i] - gama[f][n][i] * alpha[n][i][p])
                        for n in range(len(self.node_list))
                        for p in range(len(self.package_list))
                        for i in range(Zn[n]))

        result = sum(lambd[f] * (tp[f] + td[f] + ti[f]) for f in range(len(self.function_list)))
        return result



    def zygote_generation_n(self, y, n):
        # ?????????n???????????????????????????
        self.node_list[n].packages.clear()
        self.node_list[n].wants_download_packages.clear()
        self.node_list[n].memory_r = self.memory[n]
        self.node_list[n].disk_R = self.Disk[n]

        function_n = [] # ??????n??????function?????????????????????y
        for f in self.function_list:
            if y[f.id][n] == 1:
                function_n.append(f)
        if len(function_n) == 0: return []
        package_n = self.Statistics(function_n)

        for p in package_n:
            package_n[p] = package_n[p]*(p.import_time[n]+p.download_time[n])/p.size
        package_n_list = sorted(package_n.items(), key=lambda x: x[1], reverse=True)
        for p in package_n_list:
            self.node_list[n].wants_download_packages.append(p[0])
        Container_pool_n = [] #??????n?????? Container???
        if self.node_list[n].memory_r >= self.node_list[n].Bn:
            a = Container(len(Container_pool_n))
            a.want_import_packages = copy(package_n_list)
            self.node_list[n].memory_r -= self.node_list[n].Bn
            a.priority = a.want_import_packages[0][1]
            Container_pool_n.append(a)
            a.functions = copy(function_n)
            a.size = self.node_list[n].Bn
        else:
            return []
        while True:
            container = self.Find_max_priority_container(Container_pool_n)
            if container.priority < 0:
                break
            issucces = False
            tempra=copy(container.want_import_packages)
            for p in tempra:
                tem = copy(container.packages)
                tem.append(p[0])
                a = Container(len(Container_pool_n))
                a.packages = copy(tem)
                a.size += self.node_list[n].Bn
                for h in a.packages:
                    a.size += h.size
                kpl = copy(container.functions)
                for f in kpl:
                    need = []
                    for kl in f.need_packages:
                        need.append(self.package_list[kl])
                    if set(tem) <= set(need):
                        a.functions.append(f)
                        container.functions.remove(f)
                if len(container.functions) == 0:
                    if self.node_list[n].memory_r+container.size >= a.size and len(a.functions) != 0:

                        tmp = copy(container.want_import_packages)
                        tmp.remove(p)
                        a.want_import_packages = copy(tmp)
                        if len(a.want_import_packages)!=0:
                            a.priority = a.want_import_packages[0][1]
                        else:
                            a.priority = -999
                        Container_pool_n.append(a)
                        self.node_list[n].memory_r = self.node_list[n].memory_r-a.size+container.size
                        issucces = True
                        container.want_import_packages.remove(p)
                        if len(container.want_import_packages) != 0:
                            container.priority = container.want_import_packages[0][1]
                        else:
                            container.priority = -9999
                    else:
                        for hj in a.functions:
                            container.functions.append(hj)
                        container.want_import_packages.remove(p)
                        if len(container.want_import_packages)!=0:
                            container.priority = container.want_import_packages[0][1]
                        else:
                            container.priority = -9999
                else:
                    if self.node_list[n].memory_r >= a.size and len(a.functions) != 0:
                        tmp = copy(container.want_import_packages)
                        tmp.remove(p)
                        a.want_import_packages = copy(tmp)
                        if len(a.want_import_packages) != 0:
                            a.priority = a.want_import_packages[0][1]
                        else:
                            a.priority = -999
                        Container_pool_n.append(a)
                        self.node_list[n].memory_r-=a.size
                        issucces = True
                        if len(container.want_import_packages) != 0:
                            container.priority = container.want_import_packages[0][1]
                        else:
                            container.priority = -9999
                    else:
                        for hj in a.functions:
                            container.functions.append(hj)
                        if len(container.want_import_packages) != 0:
                            container.priority = container.want_import_packages[0][1]
                        else:
                            container.priority = -9999
            if issucces:
                if len(container.functions) == 0:
                    Container_pool_n.remove(container)
            else:
                break
        # ????????????????????????????????????root??????????????????????????????????????????function????????????????????????????????????package,??????????????????,?????????function???????????????.
        Container_pool = copy(Container_pool_n)
        for c in Container_pool:
            if len(c.packages) == 0:
                self.node_list[n].memory_r += c.size
                Container_pool_n.remove(c)

        # ????????????x??????????????????package?????????????????????
        # ?????????????????????????????????package?????????????????????
        # ???????????????????????????????????????package?????????????????????????????????????????????????????????????????????
        for c in Container_pool_n:
            for pa in c.packages:
                if pa not in self.node_list[n].packages:
                    self.node_list[n].packages.append(pa)
                    self.node_list[n].wants_download_packages.remove(pa)
                    self.node_list[n].disk_R -= pa.size
        for pk in self.node_list[n].wants_download_packages:
            if self.node_list[n].disk_R >= pk.size:
                self.node_list[n].packages.append(pk)
                self.node_list[n].disk_R -= pk.size
        return Container_pool_n

    def Find_max_priority_container(self, Container_pool_n):
        # ?????????????????????????????????????????????
        max = Container_pool_n[0]
        for z in Container_pool_n:
            if z.priority>max.priority:
                max = z
        return max

    def Statistics(self, functions_n):
        # ??????????????????function?????????package????????????????????????????????????.
        packages={}
        for f in functions_n:
            for p in f.need_packages:
                if self.package_list[p] in packages:
                    packages[self.package_list[p]] = packages[self.package_list[p]]+1
                else:
                    packages[self.package_list[p]] = 1

        return packages

    def gener_y(self):
        y = [[0 for n in range(len(self.node_list))] for f in range(len(self.function_list))]
        for n in self.node_list:
            for f in n.functions:
                y[f.id][n.node_id] = 1
        return y
    def Greedy(self):
        y = self.greedy_y()
        print(y)
        result, x, gamma, alpha, z, Zn = self.zygote_generation(y)
        print(result)
        return result

if __name__=="__main__":
    a = prewarm()
    for j in range(len(a.function_list)):
        a.function_list[j].request_rate = a.function_list[j].request_rate * 1.6
    a.Greedy()