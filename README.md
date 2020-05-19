# storage-topo-ansible

A hacky PoC for generating a clustered storage topology using data from Netbox.

Netbox is a CMDB that folks can use to maintain an inventory of hosts in
datacenters. Netbox can be maintained using on-host agents. Machines can be
given text-based metadata tags, assigned roles, etc.

The question we're trying to answer with this PoC is: if we have a bunch of
hosts in Netbox that are tagged to be used for a clustered storage solution, can
we use Ansible to arrange those into many clusters for us?

The answer is 'yes,' and this small Ansible inventory plugin shows how this can
be done with some level of configurability.

## Example

I stood up a Netbox instance on my laptop and added nine hosts across three DCs
and three racks. I then dumped its configuration using the Netbox Ansible
inventory plugin (`netbox_inv.yml`, `netbox_inv.json`).

`play.yml` includes configuration for the prototype inventory plugin. The Netbox
inventory plugin only has simple rules for grouping hosts. A large scale storage
system likely has its own rules for grouping hosts. These rules need to account
for cluster size and availability characteristics like host location.

Tunables:
- number of cluster members
- racks per DC that each cluster must use
- hosts per rack that each cluster must use
- data source (assuming Netbox may not always be the data source)

Example invocation:
```
$ ansible-inventory -i play.yml --playbook-dir ./ --list
{
    "_meta": {
        "hostvars": {
            "stor0": {
                "datacenter": "central-1a",
                "rack": "rack0"
            },
            "stor1": {
                "datacenter": "central-1a",
                "rack": "rack0"
            },
            "stor2": {
                "datacenter": "central-1a",
                "rack": "rack0"
            },
            "stor3": {
                "datacenter": "central-1b",
                "rack": "rack0"
            },
            "stor4": {
                "datacenter": "central-1b",
                "rack": "rack0"
            },
            "stor5": {
                "datacenter": "central-1b",
                "rack": "rack0"
            },
            "stor6": {
                "datacenter": "central-1c",
                "rack": "rack0"
            },
            "stor7": {
                "datacenter": "central-1c",
                "rack": "rack0"
            },
            "stor8": {
                "datacenter": "central-1c",
                "rack": "rack0"
            }
        }
    },
    "all": {
        "children": [
            "cluster0",
            "ungrouped"
        ]
    },
    "cluster0": {
        "hosts": [
            "stor0",
            "stor1",
            "stor2",
            "stor3",
            "stor4",
            "stor5",
            "stor6",
            "stor7",
            "stor8"
        ]
    }
}
```

In this example we have a nine-node cluster with three nodes in each rack and
one rack per DC. This creates one cluster from the nine nodes in the Netbox
inventory. The per-host metadata is maintained as hostvars for use in
deployments. We could presumably add host IP addresses or any other Netbox
metadata here as well.
