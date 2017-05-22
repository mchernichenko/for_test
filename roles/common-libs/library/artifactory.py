#!/usr/bin/python
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
    'status': ['stableinterface'],
    'supported_by': 'core',
    'version': '1.0'
}

def main():
    argument_spec = url_argument_spec()
    argument_spec.update(dict(
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        check_invalid_arguments=False,
        add_file_common_args=True)

if __name__ == '__main__':
    main()