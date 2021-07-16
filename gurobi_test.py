# from gurobipy import *
#
# m = Model("test")
# x1=m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=99999999999,name="x1")
# x2=m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=99999999999,name="x2")
# m.addConstr(x1+x2<=3,"c1")
# m.addConstr(4*x1+x2<=9)
# m.setObjective(2*x1*x1-4*x1*x2+4*x2*x2-6*x1-3*x2*x1,GRB.MINIMIZE)
# # m.setParam('nonconvex', 2)
# m.optimize()
# for v in m.getVars():
#     print('%s %g' % (v.varName, v.x))
# print('obj:%g' % m.objval)
from gurobipy import * # 导入
# 定义一个模型
m = Model()
#  设定一些参数 求解时长，精度等
m.setParam('nonconvex', 2)
# m.setParam('MIPGap', 0.0001)
# m.setParam('TimeLimit', 100)
# 定义优化变量
x1 = m.addVar(vtype=GRB.CONTINUOUS, lb=20, ub=30, name="x1")
x2 = m.addVar(vtype=GRB.CONTINUOUS, lb=20, ub=30, name="x2")
# 设定目标函数
m.setObjective(x1 * x2, GRB.MAXIMIZE)# 求最大问题 or 求最小问题
m.update()
# 添加约束 可以在设定目标函数前 或者后都可以
c_x = LinExpr()
c_x -=x1
c_x -=x2
m.addConstr(c_x<=50)
m.update()
# 进行求解
m.write('assign.lp')# 问题打印
m.optimize()
# 结果导出
if m.solCount == 0:
     print("Model is infeasible")
     m.computeIIS()
     m.write("model_iis.ilp")# 出问题无法满足的约束与残差可以打印出来debug
print('optimal solution:{} {}'.format(x1,x2))
x1_output = x1.x
x2_output = x2.x# 取出变量最优值到python变量里
