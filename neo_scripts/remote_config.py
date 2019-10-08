#!/usr/bin/python3

import sys
import os
import json
import pyexcel_ods

cfg_file_path = "/opt/config_sch.txt"


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


def main():
    data = pyexcel_ods.get_data('/opt/data/KAIS_KRO.ods')['2018-neo-integr-3']
    data.pop(0)
    region = (str(input('Введите район: '))).lower()
    state = (str(input('Введите режим конфигурации (local / remote): '))).lower()
    print('Start.')
    for sch in data:
        if not sch:
            continue
        s = get_info(sch)

        if s['Reg'] != region:
            continue
        print('### Sch', s['SchNumb'], '###')
        if state == 'local':
            with open('/opt/data/local_config', 'r') as local_config_file:
                for line in local_config_file:
                    os.system(line.format(lo=s['IPlo'], reg=s['Reg']))
        elif state == 'remote':
            with open('/opt/data/remote_config', 'r') as remote_config_file:
                cmd = []
                for line in remote_config_file:
                    cmd.append(line)
        else:
            print('Не верный формат. Досвидания.')
        print('### Configuration finished ###')
    return 0


if __name__ == '__main__':
    main()
