import json
import itertools
from ansible.plugins.inventory import BaseInventoryPlugin

DOCUMENTATION = r'''
    name: storcluster 
    plugin_type: inventory
    short_description: Returns Ansible inventory from Netbox JSON
    description: Returns Ansible inventory from Netbox JSON
    options:
      plugin:
          description: Smaug-Netbox inventory
          required: true
          choices: ['test']
      path_to_inventory_json:
        description: Location of the Netbox JSON
        required: true
    cluster_size:
        description: Count of nodes per cluster
        required: true
    hosts_per_rack:
        description: Count of hosts to be used from a given rack
        required: true
    racks_per_dc:
        description: Count of racks per DC to be used per cluster
        required: true
    source:
        description: Inventory source (e.g. 'netbox-json')
        required: true
'''


class InventoryModule(BaseInventoryPlugin):

    NAME = 'storcluster'

    def verify_file(self, path):
        '''
        XXX: Not sure what to do here.
        '''
        return True

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        self.inventory = inventory
        self.loader = loader
        self.path = path
        self.cache = cache

        config = self._read_config_data(path)

        self.cluster_size = config['cluster_size']
        self.racks_per_dc = config['racks_per_dc']
        self.hosts_per_rack = config['hosts_per_rack']

        netbox_inventory_file = open(config['path_to_inventory_json'], "r")
        netbox_inventory = json.loads(netbox_inventory_file.read())

        hostvars = netbox_inventory['_meta']['hostvars']

        region = {}

        for host in hostvars:
            print(host, hostvars[host])
            datacenter = hostvars[host]['sites'][0]
            rack = hostvars[host]['racks'][0]

            if datacenter not in region:
                region[datacenter] = {}

            if rack not in region[datacenter]:
                region[datacenter][rack] = []
            region[datacenter][rack].append(host)

        self.region = region

        for i in itertools.count():
            cluster = self._gen_cluster()
            if cluster == {}:
                break
            self._assign_roles(f'cluster{i}', cluster)

        pass

    def _gen_cluster(self):
        selection = {}
        for datacenter in self.region:
            dc = self.region[datacenter]
            if len(dc.keys()) < self.racks_per_dc:
                continue
            for rack in dc:
                r = dc[rack]
                if len(r) < self.hosts_per_rack:
                    continue
                for host in range(self.hosts_per_rack):
                    if datacenter not in selection:
                        selection[datacenter] = {}
                    if rack not in selection[datacenter]:
                        selection[datacenter][rack] = []
                    selection[datacenter][rack].append(r[host])

        return selection

    def _assign_roles(self, group, cluster):
        for datacenter in cluster:
            dc = cluster[datacenter]
            for rack in dc:
                r = dc[rack]
                for host in r:
                    self.inventory.add_group(group)
                    self.inventory.add_host(host, group)

                    self.inventory.set_variable(host, 'datacenter', datacenter)
                    self.inventory.set_variable(host, 'rack', rack)

                    self.region[datacenter][rack].remove(host)


