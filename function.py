
class function:
    def __init__(self, id, cpu_resource_need, request_rate):
        self.id = id
        self.need_packages = []
        self.cpu_resource_need = cpu_resource_need
        self.request_rate = request_rate
        self.value = {}
        self.preference_list = []
        self.transfer = [0, 0, 0, 9999]
        self.similarity = {}