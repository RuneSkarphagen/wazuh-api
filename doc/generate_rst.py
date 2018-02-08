#!/usr/bin/env python

# Created by Wazuh, Inc. <info@wazuh.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

# Quick script to create an rst file from documentation generated by apidoc

# Requirements
# https
# Auth: foo:bar

import json
import sys

TIMEOUT = 30  # cURL TIMEOUT. 0 to disable "example response"

### Hardcoded text ###
rst_header = '.. _api_reference:\n\n'
warning="\n.. Do not modify this file manually. It is generated automatically.\n\n"
introduction = "Reference\n======================\nThis API reference is organized by resources:\n\n{0}\nAlso, it is provided an `Request List`_ with all available requests.\n\n.. _request_list:\n"
str_request_list = 'Request List'
section_separator = '-'*40
subsection_separator = '+'*40
subsubsection_separator = '~'*40
str_request = '**Request**:'
str_parameter = '**Parameters:**'
str_example_req = '**Example Request:**'
str_example_res = '**Example Response:**'

hardcoded_items = {
        # GET - /manager/logs
        'GetManagerLogs': {"error":0,"data":{"totalItems":16480,"items":["2016/07/15 09:33:49 ossec-syscheckd: INFO: Syscheck scan frequency: 3600 seconds","2016/07/15 09:33:49 ossec-syscheckd: INFO: Starting syscheck scan (forwarding database).","2016/07/15 09:33:49 ossec-syscheckd: INFO: Starting syscheck database (pre-scan).","2016/07/15 09:33:42 ossec-logcollector: INFO: Started (pid: 2832).","2016/07/15 09:33:42 ossec-logcollector: INFO: Monitoring output of command(360): df -P"]}},

        # GET - /manager/stats
        'GetManagerStats': {"error":0,"data":[{"hour":5,"firewall":0,"alerts":[{"times":4,"sigid":5715,"level":3},{"times":2,"sigid":1002,"level":2},{"...":"..."}],"totalAlerts":107,"syscheck":1257,"events":1483},{"...":"..."}]},

        # GET - /manager/stats/hourly
        'GetManagerStatsHourly': {"error":0,"data":{"averages":[100,357,242,500,422,"...",123],"interactions":0}},

        # GET - /manager/stats/weekly
        'GetManagerStatsWeekly': {"error":0,"data":{"Wed":{"hours":[223,"...",456],"interactions":0},"Sun":{"hours":[332,"...",313],"interactions":0},"Fri":{"hours":[131,"...",432],"interactions":0},"Tue":{"hours":[536,"...",345],"interactions":0},"Mon":{"hours":[444,"...",556],"interactions":0},"Thu":{"hours":[888,"...",123],"interactions":0},"Sat":{"hours":[134,"...",995],"interactions":0}}},

        # PUT - /agents/restart
        'PutAgentsRestart': {"error":0,"data":"Restarting all agents"},

        # PUT - /agents/restart:agent_id
        'PutAgentsRestartId': {"error":0,"data":"Restarting agent"},

        # DELETE - /rootcheck
        'DeleteRootcheck': {"error":0,"data":"Rootcheck database deleted"},

        # DELETE - /rootcheck/:agent_id
        'DeleteRootcheckAgentId': {"error":0,"data":"Rootcheck database deleted"},

        # DELETE - /syscheck
        'DeleteSyscheck': {"error":0,"data":"Syscheck database deleted"},

        # DELETE - /syscheck/:agent_id
        'DeleteSyscheckAgentId': {"error":0,"data":"Syscheck database deleted"},

        # PUT /syscheck
        'PutSyscheck' : {"error":0,"data":"Restarting Syscheck/Rootcheck on all agents"},

        # PUT /rootcheck
        'PutRootcheck' : {"error":0,"data":"Restarting Syscheck/Rootcheck on all agents"},

        # GET /agents/groups/:group_id/files/:filename
        'GetAgentGroupFile' : {"error":0,"data":{"controls":[{"...":"..."},{"reference":"CIS_Debian_Benchmark_v1.0pdf","name":"CIS - Testing against the CIS Debian Linux Benchmark v1","condition":"all required","checks":["f:/etc/debian_version;"]}]}},

        # GET /agents/outdated
        'GetOutdatedAgents' : {"error":0,"data":{"totalItems":2,"items":[{"version": "Wazuh v3.0.0","id": "003","name": "main_database"},{"version": "Wazuh v3.0.0","id": "004","name": "dmz002"}]}},

        # PUT /agents/:agent_id/upgrade
        'PutAgentsUpgradeId' : {"error": 0,"data": "Upgrade procedure started"},

        # PUT /agents/:agent_id/upgrade_custom
        'PutAgentsUpgradeCustomId' : {"error": 0,"data": "Installation started"},

        # GET /agents/:agent_id/upgrade_result
        'GetUpgradeResult' : {"error": 0,"data": "Agent upgraded successfully"},

        # POST /agents/restart
        'PostAgentListRestart' : {"error": 0,"data": "All selected agents were restarted"},

        # GET /syscheck/:agent_id
        'GetSyscheckAgent' : {"error":0,"data":{"totalItems":2762,"items":[{"sha1":"4fed08ccbd0168593a6fffcd925adad65e5ae6d9","group":"root","uid":0,"scanDate":"2017-03-02 23:43:28","gid":0,"user":"root","file":"!1488498208 /boot/config-3.16.0-4-amd64","modificationDate":"2016-10-19 06:45:50","octalMode":"100644","permissions":"-rw-r--r--","md5":"46d43391ae54c1084a2d40e8d1b4873c","inode":5217,"event":"added","size":157721},{"sha1":"d48151a3d3638b723f5d7bc1e9c71d478fcde4e6","group":"root","uid":0,"scanDate":"2017-03-02 23:43:26","gid":0,"user":"root","file":"!1488498206 /boot/System.map-3.16.0-4-amd64","modificationDate":"2016-10-19 06:45:50","octalMode":"100644","permissions":"-rw-r--r--","md5":"29cc12246faecd4a14d212b4d9bac0fe","inode":5216,"event":"added","size":2679264}]}},

        # GET /agents/purgeable/:timeframe
        'GetAgentsPurgeable' : {"error":0,"data":{"items":[{"id":"001","name":"test1"},{"id":"002","name":"test2"}],"timeframe":104400}},

        # POST /agents/purge
        'PostAgentsPurge' : {"error":0,"data":{"totalItems":2,"items":[{"id":"001","name":"test1"},{"id":"002","name":"test2"}],"timeframe":104400}}
    }
### ### ###


### Aux functions ###
try:
    from subprocess import check_output
except ImportError:
    def check_output(arguments, stdin=None, stderr=None, shell=False):
        temp_f = mkstemp()
        returncode = call(arguments, stdin=stdin, stdout=temp_f[0], stderr=stderr, shell=shell)
        close(temp_f[0])
        file_o = open(temp_f[1], 'r')
        cmd_output = file_o.read()
        file_o.close()
        remove(temp_f[1])

        if returncode != 0:
            error_cmd = CalledProcessError(returncode, arguments[0])
            error_cmd.output = cmd_output
            raise error_cmd
        else:
            return cmd_output

def insert_row(fields, sizes, highlight=False):
    row = ''
    for i in range(len(fields)):
        if i == 0 and highlight:
            row += '| ``' + fields[i] + '``' + ' '*(sizes[i]-len(fields[i])-1-2-2)
        else:
            row += '| ' + fields[i] + ' '*(sizes[i]-len(fields[i])-1)
    row += '|' +'\n'

    return row

def insert_separator(sizes, sep='-'):
    row = ''
    for size in sizes:
        row += '+' + sep*size
    row += '+' +'\n'

    return row

def create_table(headers, rows, sizes):
    output = ''
    output += insert_separator(sizes)
    output += insert_row(headers, sizes)
    output += insert_separator(sizes, '=')
    for row in rows:
        fields = [row['field'], row['type'], row['description'].replace('<p>', '').replace('</p>', '')]
        output += insert_row(fields, sizes, not row['optional'])

        if 'allowedValues' in row:
            output += insert_row([' ', ' ', ' '], sizes)
            output += insert_row([' ', ' ', 'Allowed values:'], sizes)
            output += insert_row([' ', ' ', ' '], sizes)
            for value in row['allowedValues']:
                output += insert_row([' ', ' ', '- {0}'.format(value[1:-1])], sizes)

        output += insert_separator(sizes)
    return output
### ### ###

if __name__ == "__main__":
    alerts = []
    hardcoded = []
    docu_file_json = './build/html/api_data.json'

    # Generate docu with apidoc
    try:
        # wazuh-api: apidoc -i ../ -o ./build/html -c . -f js -e node_modules
        output = check_output(['apidoc', '-i', '../', '-o', './build/html', '-c', '.', '-f', 'js', '-e', 'node_modules'])
        print("\nAPIDOC:")
        print(output)
        with open(docu_file_json) as data_file:
            docu = json.load(data_file)
    except Exception as e:
        print("Error: {0}".format(e))
        sys.exit(1)

    # Group by section and subsection
    sections = {}
    request_list = {}

    for req in docu:
        ss = req['group']  # subsection
        if ss.startswith('_'):
            continue

        s = req['filename'].split('/')[-1][:-3]  # section

        if s not in sections:
            sections[s] = {}
            request_list[s] = []

        if ss in sections[s]:
            sections[s][ss].append(req)
        else:
            sections[s][ss] = [req]

        request_list[s].append(['{0} {1}'.format(req['type'].upper(), req['url']), req['title']])

    # Generate RST
    try:
        rst_output = sys.argv[1]
    except:
        rst_output = './build/api_reference.rst'

    print("\nOutput:")
    print(rst_output + '\n')
    f = open(rst_output, 'w')

    # Header
    f.write(rst_header)
    f.write(warning)

    # Introduction
    secs = ""
    for req in sorted(request_list.keys()):
        secs += '* `{0}`_\n'.format(req.title())
    f.write(introduction.format(secs))

    # Request list
    f.write('\n{0}\n'.format(str_request_list))
    f.write('---------------------------------' + '\n\n')
    for req in sorted(request_list.keys()):
        f.write('`{0}`_\n'.format(req.title()))
        for item in sorted(request_list[req]):
            f.write('\t* {0}  (`{1}`_)\n'.format(item[0], item[1]))
        f.write('\n')

    for s in sorted(sections.keys()):
        print(s.title())

        # Section
        f.write(s.title() + '\n')
        f.write(section_separator + '\n')

        for ss in sorted(sections[s].keys()):
            print('\t' + ss)

            # Subsection
            f.write(ss + '\n')
            f.write(subsection_separator + '\n\n')

            for item in sorted(sections[s][ss], key = lambda o: o.get('title')):
                print('\t\t{0} - {1}'.format(item['type'].upper(), item['url']))

                # Title and description
                f.write(item['title'] + '\n')
                f.write(subsubsection_separator + '\n')
                f.write(item['description'].replace('<p>', '').replace('</p>', '') + '\n')

                # Request
                f.write('\n{0}\n\n'.format(str_request))
                f.write('``{0}`` ::\n\n\t{1}\n'.format(item['type'].upper(), item['url']))

                # Parameters
                if 'parameter' in item:
                    rows = []
                    f.write('\n{0}\n\n'.format(str_parameter))
                    params = item['parameter']['fields']['Parameter']
                    table = create_table(['Param', 'Type', 'Description'], params, [20, 15, 200])
                    f.write(table)
                f.write('\n')

                # Examples
                msg_end = '\t{0} - {1}'.format(item['type'].upper(), item['url'])
                for example in item['examples']:
                    # Example Request
                    f.write(str_example_req + '\n')
                    f.write('::\n')
                    f.write('\n\t{0}\n\n'.format(example['content']))

                    # Example Response
                    if TIMEOUT != 0:
                        hardcoded_output = True if '*' in example['title'] else False

                        if hardcoded_output:
                            item_id = item['name']
                            if item_id in hardcoded_items:
                                output = json.dumps(hardcoded_items[item_id], indent=4)
                                hardcoded.append(msg_end)
                            else:
                                output = "ToDo - Hardcoded output\n"
                                alerts.append(msg_end + " -> " + output)
                        else:
                            try:
                                # Prepare command
                                command = []
                                for arg in example['content'].split(' '):
                                    start = 0
                                    end = len(arg)

                                    if arg[0] == '\'' or arg[0] == '"':
                                        start += 1
                                    if arg[-1] == '\'' or arg[-1] == '"':
                                        end -= 1

                                    command.append(arg[start:end])

                                command.extend(['--connect-timeout', str(TIMEOUT)])

                                # Get request output
                                output = check_output(command)
                            except Exception as e:
                                output = "ToDo - Error output\n"
                                alerts.append(msg_end + " -> " + output)
                    else:
                        output = "ToDo - Testing\n"
                        alerts.append(msg_end + " -> " + output)

                    f.write(str_example_res + '\n')
                    f.write('::\n')
                    for line in output.split('\n'):
                        f.write('\n\t{0}'.format(line))
                    f.write('\n')
                    # End Example Response

                f.write('\n')  # for examples
            f.write('\n')  # for item in subsection
        f.write('\n')  # for subsection

f.close()



if hardcoded:
    print("\n\nHardcoded items:\n")
    for hc in hardcoded:
        print(hc)

if alerts:
    print('\n\n' + '*'*50)
    print("There are no example responses for these requests:\n")
    for alert in alerts:
        print(alert)
    print('*'*50)

print("\nDone.\n\n")
