#!/usr/bin/python
#IMPORTING MODULES
from optparse import OptionParser
import subprocess
import os
import sys
import shlex
import re
#SETTINGS
#SEND OUTPUT TO /dev/null
FNULL = open(os.devnull, 'w')
status = {
    'vgstatus': '',
    'lvstatus': '',
    'pstatus': '',
    'hstatus': '',
    'fsstatus': '',
    'gsstatus': ''
}
fsize = ''
extsize = ''
FSystem = ''
#USER
USER = 'siddhu'
COLL_LOC = '/mnt/c/Users/cdasari/Documents/python'
#OPTIONS
parser = OptionParser()
parser.add_option('-v', '--vgname', dest='vgname', help='Enter Volume Group name')
parser.add_option('-l', '--lvname', dest='lvname', help='Enter LV Name')
parser.add_option('-H', '--host', dest='host', help='Hostname')
parser.add_option('-f', '--file', dest='file', help='Host file which contains list for hostnames')
parser.add_option('-s', '--size', dest='size', help='Size to extent lvm')
(opts, args) = parser.parse_args()
#CLASS EXTEND
class EXTEND:
    #INIT Funtion
    def __init__(self,vgname,lvname,host,size):
        self.vgname = str(vgname)
        self.lvname = str(lvname)
        self.host = str(host)
        self.size = str(size)
    #FUNTIONS
    #PRECHECKS
    def CHECK_DUPLICATES(self,host):
        print('SCRIPT WILL REMOVE IF ANY DUPLICATE HOSTNAMES FOUND IN %s FILE' %host)
        intake = raw_input('DO YOU WANT TO CONTINUE [Y/n] ')
        if intake != 'Y' and intake != 'y':
            print('TERMINATING...')
            exit(-1)
        else:        
            lines = set()
            for line in open(host):
                if line not in lines:
                    lines.add(line)
            with open(host,'w') as f:
                for line in lines:
                    f.write(line)
    def CHECK_HOST(self,host):
        global status
        print('VALIDATING %s' %host)
        host = host.rstrip()
        cmd = ['ping', '-c1', '-w2', '{}'.format(host)]
        p1 = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p1.communicate()[0]
        out = p1.returncode
        if out == 0:
            print(u'\n\033[1;32HOSTNAME\t\t\t=\t{} \N{check mark}'.format(host))
            status['hstatus'] = 0
        else:
            print(u'\nHOSTNAME\t\t\t=\t{} \N{BALLOT X}'.format(host))
            status['hstatus'] = 1
    def SSH_HOST(self,host):
        host = str(host)
        cred = '{}@{}'.format(USER,host)
        cmd1 = cred.strip()
        return cmd1
    def CHECK_PLATFORM(self,host,cmd1):
        #THIS FUNTION WILL CHECK PLATFORM TYPE
        #p1 will check the platform type and send output to /dev/null
        global status
        host = host.rstrip()
        cmd2 = 'sudo dmidecode -s system-product-name'
        cmd = ['ssh','-t', '{}' .format(cmd1), "{}" .format(cmd2)]
        p1 = subprocess.Popen(cmd,shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p1.stdout.readline()
        out = out.strip()
        if out == 'VMware Virtual Platform':
            print(u'\nPLATFORM TYPE\t\t\t=\t{} \N{check mark}'.format(out))
            status['pstatus'] = 0
        else:
            print(u'\nPLATFORM TYPE\t\t\t=\tNot Virtual \N{BALLOT X}')
            status['pstatus'] = 1
    def CHECK_VG(self,host):
        host = host.strip()
        global status
        global fsize
        cmd = 'grep -w vgs.[0-9]={} {}/{}.txt' .format(opts.vgname,COLL_LOC,host)
        cmd = cmd.strip()
        p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        FS = p1.communicate()[0]
        out = p1.returncode
        FS = FS.split(',')
        if out != 0:
            print(u"\nVOLUME GROUP\t\t\t=\t{} \N{BALLOT X}" .format(opts.vgname))
            fsize = 'Unknown'
            status['vgstatus'] = 1
        else:
            print(u"\nVOLUME GROUP\t\t\t=\t%s \N{check mark}" %opts.vgname)
            fsize = FS[6]
            status['vgstatus'] = 0
    def CHECK_SIZE(self,host):
        global status
        global fsize
        global extsize
        host = host.strip()
        fsize = fsize.strip()
        ifsize =fsize.upper()
        gsize = opts.size
        igsize = gsize.upper()

        #IF size contain '<' strip off '<'
        if not re.match('[0-9]', fsize[0]):
            fsize = fsize[1:]
            ifsize =fsize.upper()

        # FREE SIZE CONVERSION
        if fsize[-1] == 'g' or fsize[-1] == 'G':
            fsize = 1024 * float(fsize[:-1])
        elif fsize[-1] == 'm' or fsize[-1] == 'M':
            fsize = float(fsize[:-1])
        else:
            ifsize = 'Unknown Format'

        # EXTENT SIZE CONVERSION
        if gsize[-1] == 'g' or gsize[-1] == 'G':
            gsize = 1024 * float(gsize[:-1])
        elif gsize[-1] == 'm' or gsize[-1] == 'M':
            gsize = float(gsize[:-1])
        else:
            gsize = 'Unknown'

        if fsize > 0 and isinstance(gsize, basestring):
            print(u'\nFREE SIZE\t\t\t=\t{} \N{check mark}' .format(ifsize))
            status['fsstatus'] = 0
            print(u'\nEXTEND SIZE\t\t\t=\t{} \N{BALLOT X}' .format(igsize))
            status['gsstatus'] = 1
        elif fsize > 0 and fsize > gsize and not isinstance(gsize, basestring):
            print(u'\nFREE SIZE\t\t\t=\t{} \N{check mark}' .format(ifsize))
            status['fsstatus'] = 0
            print(u'\nEXTEND SIZE\t\t\t=\t{} \N{check mark}' .format(igsize))
            status['gsstatus'] = 0
            extsize = igsize
        else:
            print(u'\nFREE SIZE\t\t\t=\t{} \N{BALLOT X}' .format(ifsize))
            status['fsstatus'] = 1
            print(u'\nEXTEND SIZE\t\t\t=\t{} \N{BALLOT X}' .format(igsize))
            status['gsstatus'] = 1
    def CHECK_LV(self,host):
        global status
        global FSystem
        host = host.strip()
        cmd = 'grep -w df.[0-9]=/dev/mapper/{}-{} {}.txt' .format(opts.vgname, opts.lvname, host)
        p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        FS = p1.communicate()[0]
        out = p1.returncode
        FS = FS.split()
        if out != 0:
            print(u"\nLOGICAL VOLUME\t\t\t=\t/dev/{}/{} \N{BALLOT X}" .format(opts.vgname,opts.lvname))
            print(u"\nFILESYSTEM TYPE\t\t\t=\tUnknown \N{BALLOT X}")
            status['lvstatus'] = 1
        else:
            print(u"\nLOGICAL VOLUME\t\t\t=\t/dev/{}/{} \N{check mark}" .format(opts.vgname,opts.lvname))
            print(u"\nFILESYSTEM TYPE\t\t\t=\t{} \N{check mark}" .format(FS[1]))
            FSystem = FS[1]
            status['lvstatus'] = 0
    #Execution funtions
    def EXTEND_LVM(self,host,cmd1):
        global extsize
        global FSystem
        host = host.strip()
        lvm = '/dev/{}/{}' .format(opts.vgname,opts.lvname)
        cmd2 = 'sudo lvextend -L +{} {}' .format(extsize,lvm)
        if FSystem in ['ext4','ext3']:
            cmd3 = 'sudo resize2fs -p {}' .format(lvm)
        elif FSystem in ['xfs']:
            cmd3 = 'sudo xfs_growfs {}' .format(lvm)
        cmd = ['ssh', '-t', '{}' .format(cmd1), "{} && {}" .format(cmd2,cmd3)]
        p1 = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for s in p1.stdout:
            print(s.strip())
    def CONFIRM(self):
        #USER CONFIRMATION CHECK
        inp = input("Do you want to proceed? [Y/n] ")
        if inp != 'Y' and inp != 'y':
            exit(-1)
#MAIN Funtion
def main(host):
    x = EXTEND(opts.vgname,opts.lvname,opts.size,opts.host)
    if opts.file == None:
        host = host.strip()
        cred = '{}@{}'.format(USER,host)
        cmd1 = cred.strip()
        print('==============================================================')
        x.CHECK_HOST(host)
        x.CHECK_PLATFORM(host,cmd1)
        x.CHECK_VG(host)
        x.CHECK_LV(host)
        x.CHECK_SIZE(host)
        if not all(x==0 for x in status.values()):
            print('\nUNABLE TO EXTEND LVM IN {}...'.format(host))
            for p in status:
                print(p, status[p])
        else:
            print('\nExtending LVM...\n')
            x.EXTEND_LVM(host,cmd1)
    else:
        print('CHECKING DUPLICATE HOSTNAMES IN %s FILE' %host)
        x.CHECK_DUPLICATES(host)
        f = open(host,'r')
        for i in f:
            i = str(i)
            cred = '{}@{}'.format(USER,i)
            cmd1 = cred.strip()
            print('==============================================================')
            x.CHECK_HOST(i)
            x.CHECK_PLATFORM(i,cmd1)
            x.CHECK_VG(i)
            x.CHECK_LV(i)
            x.CHECK_SIZE(i)
            if not all(x==0 for x in status.values()):
                print('\nUNABLE TO EXTEND LVM IN {}...'.format(i))
                for p in status:
                    print(p, status[p])
                continue
            print('\nExtending LVM...\n')
            x.EXTEND_LVM(i,cmd1)
#MAIN
if __name__ == '__main__':
    if opts.vgname == None or opts.lvname == None or opts.size == None:
        parser.print_help()
        exit(-1)
    elif opts.host == None and opts.file == None:
        print('Please enter hostname or host file.')
        parser.print_help()
        exit(-1)
    elif opts.host:
        host = opts.host
    elif opts.file:
        host = opts.file
    main(host)

    #vg_free_size=vgs myvg | awk '{print $7}' | sed -ne 2p | cut -c 2-