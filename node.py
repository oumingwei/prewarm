
class node:
    def __init__(self, node_id, disk_R, memory_r, cpu_resources, Bn):
        self.node_id = node_id
        self.disk_R = disk_R
        self.memory_r = memory_r
        self.cpu_resources = cpu_resources
        self.Bn = Bn
        self.Tc = []
        self.preference = [] # 对function的偏好队列
        self.functions = [] # 部署在该节点上function

        self.packages = [] # 缓存在该节点硬盘上的package
        self.wants_download_packages = [] # 节点n还想缓存的节点