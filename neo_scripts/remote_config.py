#!/usr/bin/python3

import sys
import os
import json
import pyexcel_ods
import argparse
import subprocess
import tabulate


def get_info(sch):
    s = {}
    s['Reg'] = sch[0] if len(sch) > 0 else ''
    s['SchNumb'] = sch[1] if len(sch) > 1 else ''
    s['IPlo'] = sch[2] if len(sch) > 2 else ''
    s['V10'] = sch[3] if len(sch) > 3 else ''
    s['V20'] = sch[4] if len(sch) > 4 else ''
    s['V30'] = sch[5] if len(sch) > 5 else ''
    s['ZS'] = sch[6] if len(sch) > 6 else ''
    s['OSPar'] = sch[7] if len(sch) > 7 else ''
    s['OSWeb'] = sch[8] if len(sch) > 8 else ''
    s['EMTS'] = sch[9] if len(sch) > 9 else ''
    s['PtM_Vtun'] = sch[10] if len(sch) > 10 else ''
    s['PtP_Vtun'] = sch[11] if len(sch) > 11 else ''
    s['R_Vtun'] = sch[12] if len(sch) > 12 else ''
    s['PtP_Port'] = sch[13] if len(sch) > 13 else ''
    s['PtM_Port'] = sch[14] if len(sch) > 14 else ''
    s['PtP_Core'] = sch[15] if len(sch) > 15 else ''
    s['PtM_Core'] = sch[16] if len(sch) > 16 else ''
    s['R_Core'] = sch[17] if len(sch) > 17 else ''
    s['SCCAT'] = sch[18] if len(sch) > 18 else ''
    s['Name'] = sch[19] if len(sch) > 19 else ''
    s['Address'] = sch[20] if len(sch) > 20 else ''
    s['Translit'] = sch[21] if len(sch) > 21 else ''
    s['Hostname'] = sch[22] if len(sch) > 22 else ''
    return s


def verbose(value):
    if 0 < value < 8:
        mail_verb = value // 4
        process_verb = (value % 4) // 2
        finish_verb = (value % 4) % 2
        return mail_verb, process_verb, finish_verb
    else:
        return False


def main():
    data = pyexcel_ods.get_data('/opt/data/KAIS_KRO.ods')['2018-neo-integr-3']
    data.pop(0)
    parser = argparse.ArgumentParser(description='Set mode local/remote '
                                                 'and configuration target region.')
    parser.add_argument('region', action='store', type=str, help='Set region to configure.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--remote', action='store_true', help='Set remote configuration mode.')
    group.add_argument('-l', '--local', action='store_true', help='Set local configuration mode.')
    parser.add_argument('-c', '--configure', action='store_true', help='Configuration mode for remote devices.')
    parser.add_argument('-s', '--save', action='store_true', help='Commit and save configuration on remote devices.')
    parser.add_argument('-v', action='store', dest='verbose', type=int, default=1,
                        help='Verbose mode. Print list of devices and send email. '
                             'A numeric mode is from one to four octal digits (0-7), '
                             'derived by adding up the bits with values 4, 2, and 1. '
                             '0 is without verbose, 1 is final verbose, 2 is process '
                             'verbose and 3 is mail verbose')
    args = parser.parse_args()
    final_output = {'bad_configuration': [], 'good_configuration': []}
    verbose_dict = {}
    if args.verbose:
        try:
            verbose_dict = dict(zip(['mail_verb', 'process_verb', 'finish_verb'], verbose(args.verbose)))
        except TypeError:
            print('Incorrect format verbose! Will be use default value.')
            verbose_dict = {'mail_verb': 0,
                            'process_verb': 0,
                            'finish_verb': 1}
    if verbose_dict['process_verb']:
        stdout = None
        stderr = None
    else:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
    print('Start.')
    for sch in data:
        if not sch:
            continue
        s = get_info(sch)
        if s['Reg'] != args.region:
            continue
        with open('/opt/data/exception_ip', 'r') as exception_ip_file:
            address = []
            for ip in exception_ip_file:
                address.append(ip.strip())
        if s['IPlo'] in address:
            continue
        if verbose_dict['process_verb']:
            print('### Sch', s['SchNumb'], '###')
        if args.local:
            with open('/opt/data/local_config', 'r') as local_config_file:
                for line in local_config_file:
                    reply = subprocess.run(line.format(lo=s['IPlo'], reg=s['Reg']),
                                           shell=True,
                                           stdout=stdout,
                                           stderr=stderr,
                                           encoding='utf-8')
                    if reply.returncode == 0:
                        final_output['good_configuration'].append(s['IPlo'])
                    else:
                        final_output['bad_configuration'].append(s['IPlo'])
        elif args.remote:
            with open('/opt/data/remote_config', 'r') as remote_config_file:
                cmd = []
                if args.configure:
                    cmd.append('configure')
                for line in remote_config_file:
                    cmd.append(line)
                if args.configure and args.save:
                    cmd.append('commit')
                    cmd.append('save')
                if args.configure:
                    cmd.append('exit')
            with open('/opt/data/config_sch.txt', 'w+') as config_sch_file:
                for command in cmd:
                    config_sch_file.write(command + '\n')
            run_expect = '/opt/data/config_test.exp ' + s['IPlo'] + ' /opt/data/config_sch.txt'
            reply = subprocess.run(run_expect,
                                   shell=True,
                                   stdout=stdout,
                                   stderr=stderr,
                                   encoding='utf-8')
            if reply.returncode == 0:
                final_output['good_configuration'].append(s['IPlo'])
            else:
                final_output['bad_configuration'].append(s['IPlo'])
            os.remove('/opt/data/config_sch.txt')
        else:
            print("Mode doesn't exist. Bye.")
    if verbose_dict['finish_verb']:
        print(tabulate.tabulate(final_output, headers='keys'))
    return 0


if __name__ == '__main__':
    main()
