#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
from ansible.plugins.action import ActionBase
import re

__metaclass__ = type


# Functions for sorting artifacts path in human order
def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(artifact):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split('(\d+)', artifact['path'])]


class ActionModule(ActionBase):
    TRANSFERS_FILES = False

    def _create_aql_request(self, repo, path, props={}):
        search_criteria = [
            '{{"repo": {{"$match": "{0}"}} }}'.format(repo),
            '{{"path": {{"$match": "{0}"}} }}'.format(path),
        ]

        for prop_name, prop_value in props.iteritems():
            if prop_value:
                search_criteria.append('{{ "@{0}": {{"$match": "{1}"}} }}'.
                                       format(prop_name, prop_value))
        search_string = ','.join(search_criteria)

        return """
        items.find({{
            "$and": [ {0} ]
        }}).include("repo", "path", "name", "actual_md5",
                    "actual_sha1").sort({{"$desc" : ["path"]}})
        """.format(search_string).strip()

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        release = task_vars.get('release')
        train = task_vars.get('train')
        version = None
        for grp in task_vars['group_names']:
            if '{0}_version'.format(grp) in task_vars:
                version = task_vars['{0}_version'.format(grp)]
                break
        path_version = None
        for grp in task_vars['group_names']:
            if '{0}_path_version'.format(grp) in task_vars:
                path_version = task_vars['{0}_path_version'.format(grp)]
                break

        # Get artifactory url
        url = self._task.args.get('url')
        if not url:
            url = task_vars.get('artifactory').get('search_url')
        if not url:
            result['failed'] = True
            result['msg'] = 'Artifactory URL not found in params'
            return result
        url = self._templar.template(url)

        # Get artifactory key
        apikey = self._task.args.get('api_key')
        if not apikey:
            apikey = task_vars.get('artifactory').get('api_key')
        if not apikey:
            result['failed'] = True
            result['msg'] = 'Artifactory API key not found in params'
            return result
        apikey = self._templar.template(apikey)

        # Get artifactory repo
        repo = self._task.args.get('repo')
        if not repo:
            repo = task_vars.get('artifactory').get('repo')
        if not repo:
            result['failed'] = True
            result['msg'] = 'Artifactory repository name not found in params'
            return result
        repo = self._templar.template(repo)

        # Check path in params
        path = self._task.args.get('path')
        if not path:
            result['failed'] = True
            result['msg'] = \
                'Artifactory PATH for artifact searching not found in params'
            return result
        path = self._templar.template(path)

        # Create search request
        body = self._task.args.get('body')
        if not body:
            if version:
                body = self._create_aql_request(
                    repo, path, props={'version': version})
            elif train:
                body = self._create_aql_request(
                    repo, path, props={'train': train})
            elif release:
                body = self._create_aql_request(
                    repo, path, props={'release': release})
            else:
                body = self._create_aql_request(repo, path)

        new_module_args = self._task.args.copy()
        new_module_args.update(
            dict(
                url=url,
                method='POST',
                body=body,
                headers={'X-JFrog-Art-Api': apikey},
                body_format='json'))

        result.update(
            self._execute_module(
                module_name='uri',
                module_args=new_module_args,
                task_vars=task_vars))

        # Get latest result
        if result['status'] == 200:
            if result['json']['range']['total'] > 0:
                # sort result by version in human order
                result['json']['results'].sort(key=natural_keys)

                if not version and path_version:
                    for artifact in result['json']['results']:
                        if path_version in artifact['path']:
                            result['artifact'] = artifact
                            artifact['full_path'] = '{0}/{1}/{2}'.format(
                                result['artifact']['repo'],
                                result['artifact']['path'],
                                result['artifact']['name'])
                else:
                    # get latest version
                    result['artifact'] = result['json']['results'][-1]
                    result['artifact'][
                        'full_path'] = '{0}/{1}/{2}'.format(
                            result['artifact']['repo'],
                            result['artifact']['path'],
                            result['artifact']['name'])

                if 'artifact' in result:
                    result['artifact']['found'] = True
                else:
                    result['artifact'] = {}
                    result['artifact']['found'] = False

            else:
                result['artifact'] = {}
                result['artifact']['found'] = False

        return result
