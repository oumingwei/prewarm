class Container:
    def __init__(self, id):
        self.id=id
        self.packages = [] # 容器包含哪些package
        self.functions = [] # 容器给哪些function使用
        self.priority = -1 # 导入新包的优先级，取决于将要导入的包
        self.want_import_packages = [] #想要导入的包，按优先级降序排列
        self.size = 0 #Container的大小