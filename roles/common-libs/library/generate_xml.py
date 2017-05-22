# -*- coding: utf-8 -*-
"""
Role for generate XML from YML

YAML format
root:
    nodes:
      - node1:
          attrs:
            attr1: value1
            attr2: value2
          nodes:
            - child_node1:
                attrs: ...
                nodes: ...
            - child_node2: 'text value'
      - node2:
          attrs: ...
          nodes: ...
      - node3: 'text value'
      - node4
"""

import hashlib
import os

from ansible.module_utils.basic import AnsibleModule
from lxml import etree


def get_file_md5hash(file_name):
    "Get file's hash"

    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def create_node(root_name, **kwargs):
    "Create nodes in xml tree"

    root = etree.Element(root_name)
    # Create attrs
    if 'attrs' in kwargs.keys():
        for key, value in kwargs['attrs'].iteritems():
            root.set(key, str(value).strip())

    # Create child nodes
    if 'nodes' in kwargs.keys():
        for node in kwargs['nodes']:
            if isinstance(node, dict):
                node_name = node.keys()[0]
                node_value = node[node_name]

                if isinstance(node_value, dict):
                    child = create_node(node_name, **node_value)
                    root.append(child)
                else:
                    child = etree.Element(node_name)
                    child.text = node_value
                    root.append(child)
            else:
                child = etree.Element(node)
                root.append(child)

    return root


def main():
    "Ansible module"

    module = AnsibleModule(argument_spec=dict(
        data=dict(required=True, type='dict'),
        dest=dict(required=True, type='path'),
        root_name=dict(
            required=False, default='Configuration', aliases=['root'])))

    root_name = module.params['root_name']
    data = module.params['data']
    file_name = module.params['dest']
    md5sum_before = None
    changed = False

    # If file exist, calc md5
    if os.path.exists(file_name):
        try:
            md5sum_before = get_file_md5hash(file_name)
        except IOError as e:
            module.fail_json(msg="{0}: Read file error({1}): {2}".format(
                file_name, e.errno, e.strerror))

    # Generate and save file
    root = create_node(root_name, **data)
    try:
        with open(file_name, 'w') as f:
            f.writelines(
                etree.tostring(root, pretty_print=True).encode('utf-8'))
    except IOError as e:
        module.fail_json(msg="{0}: Save file error({1}): {2}".format(
            file_name, e.errno, e.strerror))

    # calc md5 after
    md5sum_after = get_file_md5hash(file_name)
    # if md5 before != after => changed
    if md5sum_before != md5sum_after:
        changed = True

    response = {"Generate file:": file_name}
    module.exit_json(changed=changed, meta=response)


if __name__ == '__main__':
    main()
