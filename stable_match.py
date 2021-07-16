import json
import time
from copy import copy
import random

from node import node
from function import function
from package import package
from Container import Container
class prewarm:
    def __init__(self):
        self.node_list = []#N
        self.function_list = []#F
        self.package_list = []#P
        node_data = json.load(open('node.json'))
        for i in range(len(node_data["node"])):
            index = 'n' + str(i + 1)
            node1=node(node_data["node"][index]["id"],
                                       node_data["node"][index]["disk_R"],
                                       node_data["node"][index]["memory_r"],
                                       node_data["node"][index]["cpu_resources"],
                                       node_data["node"][index]["Bn"])
            for j in range(len(node_data["node"][index]["Tc"])):
                index1 = 'f'+ str(j+1)
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

        self.memory = [0 for n in range(len(self.node_list))]
        self.Disk = [0 for n in range(len(self.node_list))]
        self.cpu = [0 for n in range(len(self.node_list))]
        for n in range(len(self.node_list)):
            self.memory[n] = self.node_list[n].memory_r
            self.Disk[n] = self.node_list[n].disk_R
            self.cpu[n] = self.node_list[n].cpu_resources

    def stable_match_based(self):
        # node.preference [function的id, function在n上的价值]
        # function.preference [node_id, node的内存大小]
        for n in range(len(self.node_list)):
            self.node_list[n].functions.clear()
        # 1.计算function的value
        for f in self.function_list:

            for n in range(len(self.node_list)):
                T = 0 #计算一下package产生的时间
                size = 0
                for i in f.need_packages:

                    T+= self.package_list[i].import_time[n]+self.package_list[i].download_time[n]
                    size += self.package_list[i].size
                f.value[n] = f.request_rate*T/size
        # 2.产生偏好队列
        # 2.1function的偏好队列
        for f in self.function_list:
            for n in self.node_list:
                f.preference_list.append([n.node_id, n.memory_r])
            f.preference_list.sort(key=lambda x: x[1], reverse=True)
            # 还需要做一个调整，内存大小一样时硬盘越大的越靠前.
            for i in range(len(f.preference_list)-1):
                if f.preference_list[i][1] == f.preference_list[i+1][1]:
                    if self.node_list[f.preference_list[i + 1][0]].disk_R > self.node_list[f.preference_list[i][0]].disk_R:
                        _ = f.preference_list[i + 1]
                        f.preference_list[i + 1] = f.preference_list[i]
                        f.preference_list[i] = _
        # 2.2 产生node的preference_list
        for n in self.node_list:
            for f in self.function_list:
                n.preference.append([f.id, f.value[n.node_id]])
            n.preference.sort(key=lambda x: x[1], reverse=True)

        # 3 function向node请求，开始stable match.
        free_list = [] # 设置一个free的list, 初始化将所有的function都放入
        count = [0 for f in range(len(self.function_list))] # 记录每一个function的请求次数,开始都为0
        for f in self.function_list:
            free_list.append(f)
        while len(free_list) != 0:
            f = free_list[0]
            # function一直请求，直到配对成功为止
            while count[f.id] < len(self.node_list):
                if self.node_list[f.preference_list[count[f.id]][0]].cpu_resources >= f.cpu_resource_need * f.request_rate:
                    self.node_list[f.preference_list[count[f.id]][0]].cpu_resources -= (f.cpu_resource_need * f.request_rate)
                    self.node_list[f.preference_list[count[f.id]][0]].functions.append(f)
                    count[f.id] += 1
                    free_list.remove(f)
                    break
                else:
                    tem = []
                    fla = True
                    for _ in self.node_list[f.preference_list[count[f.id]][0]].functions:
                        if _.value[self.node_list[f.preference_list[count[f.id]][0]].node_id] < f.value[self.node_list[f.preference_list[count[f.id]][0]].node_id]:
                            tem.append(_)
                            self.node_list[f.preference_list[count[f.id]][0]].functions.remove(_)
                            self.node_list[f.preference_list[count[f.id]][0]].cpu_resources += _.cpu_resource_need *_.request_rate

                        if self.node_list[f.preference_list[count[f.id]][0]].cpu_resources >= f.cpu_resource_need * f.request_rate:
                            if sum(k.value[self.node_list[f.preference_list[count[f.id]][0]].node_id] for k in tem) < f.value[self.node_list[f.preference_list[count[f.id]][0]].node_id]:
                                fla=False
                                self.node_list[f.preference_list[count[f.id]][0]].functions.append(f)
                                self.node_list[f.preference_list[count[f.id]][0]].cpu_resources -= (f.cpu_resource_need * f.request_rate)
                                free_list.remove(f)
                                count[f.id] += 1
                                for j in tem:
                                    free_list.append(j)
                                break
                            else:
                                for j in tem:
                                    self.node_list[f.preference_list[count[f.id]][0]].functions.append(j)
                                    self.node_list[f.preference_list[count[f.id]][0]].cpu_resources -= (j.cpu_resource_need * j.request_rate)
                                break
                    if fla:
                        for j in tem:
                            self.node_list[f.preference_list[count[f.id]][0]].functions.append(j)
                            self.node_list[f.preference_list[count[f.id]][0]].cpu_resources -= (
                                            j.cpu_resource_need * j.request_rate)
                            break
                    if f not in free_list:
                        break
                    else:
                        count[f.id] += 1


        return self.gener_y()
    def gener_y(self):
        # 根据当前function的分布生成y
        y = [[0 for n in range(len(self.node_list))] for f in range(len(self.function_list))]
        for n in self.node_list:
            for f in n.functions:
                y[f.id][n.node_id] = 1
        return y
    def zygote_generation(self, y):
        # 第二阶段算法，根据stable match的结果，在每一个节点内进行package的缓存
        # 1.初始化需要求解的变量
        Zn = [0 for i in range(len(self.node_list))]
        for n in range(len(self.node_list)):
            Zn[n] = int(self.memory[n]/ self.node_list[n].Bn)
        z = [[0 for i in range(Zn[n])] for n in range(len(self.node_list))]
        gamma = [[[0 for i in range(Zn[n])] for n in range(len(self.node_list))] for f in
                 range(len(self.function_list))]
        alpha = [[[0 for p in range(len(self.package_list))] for i in range(Zn[n])] for n in
                 range(len(self.node_list))]
        x = [[0 for p in range(len(self.package_list))]for n in range(len(self.node_list))]

        Container_pool=[[]for n in range(len(self.node_list))]# 创建每个节点的容器池
        for n in range(len(self.node_list)):
            Container_pool[n] = copy(self.zygote_generation_n(y, n))# 每个节点都做zygote生成操作
        #根据生成结果来给变量赋值
        for n in range(len(self.node_list)):
            for i in Container_pool[n]:
                for f in i.functions:
                    gamma[f.id][n][i.id] = 1
                for p in i.packages:
                    alpha[n][i.id][p.id] = 1
                z[n][i.id] = 1
            for pl in self.node_list[n].packages:
                x[n][pl.id] = 1
      # 计算最终的结果
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

        H = [0 for n in range(len(self.node_list))]  # 硬盘空间
        Cn = [0 for n in range(len(self.node_list))]  # cpu资源
        M = [0 for n in range(len(self.node_list))]  # 内存空间
        Bn = [0 for n in range(len(self.node_list))]  # 创建一个容器的开销，内存
        Tc = [[0 for f in range(len(self.function_list))] for i in range(len(self.node_list))] # 拉取一个容器的时间
        for n in range(len(self.node_list)):
            H[n] = self.node_list[n].disk_R
            M[n] = self.node_list[n].memory_r
            Cn[n] = self.node_list[n].cpu_resources
            Bn[n] = self.node_list[n].Bn
            for f in range(len(self.function_list)):
                Tc[n][f] = self.node_list[n].Tc[f]
        # Cj Calculation resource size required by function j
        C = [0 for j in range(len(self.function_list))]  # function需要得CPU资源
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
        # 在节点n内进行容器生成操作
        self.node_list[n].packages.clear()
        self.node_list[n].wants_download_packages.clear()
        self.node_list[n].memory_r = self.memory[n]
        self.node_list[n].disk_R = self.Disk[n]

        function_n = [] # 节点n上的function集合，结果来自y
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
        Container_pool_n = [] #节点n上的 Container池
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
        # 需要做一个操作，就是如果root容器还在，证明这个容器里还有function，但是这个容器中没有任何package,这类容器删除,其中的function选择冷启动.
        Container_pool = copy(Container_pool_n)
        for c in Container_pool:
            if len(c.packages) == 0:
                self.node_list[n].memory_r += c.size
                Container_pool_n.remove(c)

        # 接下来对x赋值，即哪些package该被放在硬盘上
        # 首先所有被放入内存中的package都应放入硬盘上
        # 其次剩余没有被放入硬盘上的package按照优先级降序依次放入硬盘，直到硬盘容量不足。
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
        # 从容器池中找到优先级最大的容器
        max = Container_pool_n[0]
        for z in Container_pool_n:
            if z.priority>max.priority:
                max = z
        return max

    def Statistics(self, functions_n):
        # 用来统计所有function需要的package种类集合及其被使用的次数.
        packages={}
        for f in functions_n:
            for p in f.need_packages:
                if self.package_list[p] in packages:
                    packages[self.package_list[p]] = packages[self.package_list[p]]+1
                else:
                    packages[self.package_list[p]] = 1

        return packages
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
                Most_memory_node.sort(key=lambda x:x[1], reverse=True)
                for n in Most_memory_node:
                    if n[0].cpu_resources >= f.cpu_resource_need * f.request_rate:
                        n[0].functions.append(f)
                        n[0].cpu_resources -= f.cpu_resource_need * f.request_rate
                        break
        return self.gener_y()

    # def Coalitional_Game(self):
    #     # 按照自己的理解
    #     # 由于stable match 只给出了初步的一个方案，该方案存在很多不足，因此使用联盟博弈来进行调整.
    #     y = self.stable_match_based()
    #     result, x, gamma, alpha, z, Zn = self.zygote_generation(y)
    #     count=0
    #     while True:
    #         time_start=time.time()
    #         flag = False
    #         for n in self.node_list:
    #             tem_list = copy(n.functions)
    #             for f in tem_list:
    #                 for j in self.node_list:
    #                     if f not in j.functions and j.cpu_resources >= f.cpu_resource_need * f.request_rate:
    #                         j.functions.append(f)
    #                         n.functions.remove(f)
    #                         y_temp = self.gener_y()
    #                         result_temp, x_temp, gamma_temp, alpha_temp, z_temp, Zn_temp = self.zygote_generation(y_temp)
    #                         if result_temp < result:
    #                             y = copy(y_temp)
    #                             result = result_temp
    #                             j.cpu_resources -= (f.cpu_resource_need * f.request_rate)
    #                             n.cpu_resources += (f.cpu_resource_need * f.request_rate)
    #                             x = copy(x_temp)
    #                             gamma = copy(gamma_temp)
    #                             alpha = copy(alpha_temp)
    #                             z = copy(z_temp)
    #                             Zn = copy(Zn_temp)
    #                             count += 1
    #                             flag = True
    #                             break
    #                         else:
    #                             j.functions.remove(f)
    #                             n.functions.append(f)
    #         if flag == False:
    #             break
    #     time_end = time.time()



        self.show(y, x, gamma, alpha, z, Zn,result)
        print("迭代次数：", count)
        print("用时：", time_end-time_start)
        return result

    def random_y(self):
        y = [[0 for n in range(len(self.node_list))] for f in range(len(self.function_list))]
        for f in range(len(self.function_list)):
            while sum(y[f][k] for k in range(len(self.node_list))) != 1:
                for n in range(len(self.node_list)):
                    y[f][n] = random.randint(0, 1)
                    if y[f][n] == 1:
                        if self.node_list[n].cpu_resources >= self.function_list[f].cpu_resource_need * \
                                self.function_list[f].request_rate:
                            self.node_list[n].cpu_resources -= self.function_list[f].cpu_resource_need * \
                                                               self.function_list[f].request_rate
                            self.node_list[n].functions.append(self.function_list[f])
                            break
                        else:
                            y[f][n] = 0
        return y

    def Coalitional_Game(self):# 按照参考论文的思路

        y = self.random_y()
        # y = self.stable_match_based()
        #y = self.gener_y()
        result, x, gamma, alpha, z, Zn = self.zygote_generation(y)
        count=0
        while True:
            TV = [0, 0, 0, 99999]
            time_start = time.time()
            flag = False
            for n in self.node_list:
                tem_list = copy(n.functions)
                for f in tem_list:
                    for j in self.node_list:
                        f.transfer = [f.id, n.node_id, j.node_id, 9999]
                        if f not in j.functions and j.cpu_resources >= f.cpu_resource_need * f.request_rate:
                            j.functions.append(f)
                            n.functions.remove(f)
                            y_temp = self.gener_y()
                            result_temp, x_temp, gamma_temp, alpha_temp, z_temp, Zn_temp = self.zygote_generation(y_temp)
                            f.transfer[3] = result_temp - result
                            j.functions.remove(f)
                            n.functions.append(f)
                            if TV[3] > f.transfer[3] and f.transfer[3] < 0:
                                TV = copy(f.transfer)
                                flag = True
            if flag:
                count += 1
                self.node_list[TV[1]].functions.remove(self.function_list[TV[0]])
                self.node_list[TV[2]].functions.append(self.function_list[TV[0]])
                self.node_list[TV[2]].cpu_resources -= self.function_list[TV[0]].cpu_resource_need * self.function_list[TV[0]].request_rate
                y = self.gener_y()
                result, x, gamma, alpha, z, Zn = self.zygote_generation(y)
            else:
                break
        time_end = time.time()
        self.show(y, x, gamma, alpha, z, Zn, result)
        print("迭代次数：", count)
        print("用时：", time_end-time_start)
        return result
if __name__=="__main__":
    a = prewarm()
    a.Coalitional_Game()

