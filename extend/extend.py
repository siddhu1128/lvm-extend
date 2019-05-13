#!/usr/bin/python
#IMPORTING MODULES
from optparse import OptionParser
import subprocess
import os
import sys
import shlex
#SETTINGS
#SEND OUTPUT TO /dev/null
FNULL = open(os.devnull, 'w')
OUT_CMD = ''
#USER
USER = 'siddhu'
#OPTIONS
parser = OptionParser()
parser.add_option('-v', '--vgname', dest='vgname', help='Enter Volume Group name')
parser.add_option('-l', '--lvname', dest='lvname', help='Enter LV Name')
parser.add_option('-F', '--fstype', dest='fstype', help='Enter filesystem type (eg:ext3/ext4/xfs)')
parser.add_option('-H', '--host', dest='host', help='Hostname')
parser.add_option('-f', '--file', dest='file', help='Host file which contains list for hostnames')
(opts, args) = parser.parse_args()
#CLASS EXTEND
class EXTEND:
    #INIT Funtion
    def __init__(self,vgname,lvname,fstype,host):
        self.vgname = str(vgname)
        self.lvname = str(lvname)
        self.fstype = str(fstype)
        self.host = str(host)
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
        print('VALIDATING %s' %host)
        host = host.rstrip()
        cmd = ['ping', '-c1', '-w2', '{}'.format(host)]
        p1 = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p1.communicate()[0]
        out = p1.returncode
        if out == 0:
            print(u'HOSTNAME\t\t\t=\t{} \N{check mark}'.format(host))
        else:
            print(u'HOSTNAME\t\t\t=\t{} \N{BALLOT X}'.format(host))
    def SSH_HOST(self,host):
        host = str(host)
        cred = '{}@{}'.format(USER,host)
        cmd1 = cred.strip()
        return cmd1
    def CHECK_PLATFORM(self,host,cmd1):
        #THIS FUNTION WILL CHECK PLATFORM TYPE
        #p1 will check the platform type and send output to /dev/null
        host = host.rstrip()
        cmd2 = 'sudo dmidecode -s system-product-name'
        cmd = ['ssh','-t', '{}' .format(cmd1), "{}" .format(cmd2)]
        p1 = subprocess.Popen(cmd,shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #p1.communicate()[0]
        out = p1.stdout.readline()
        out = out.strip()
        if out == 'VMware Virtual Platform':
            print(u'\nPLATFORM TYPE\t\t\t=\t{} \N{check mark}'.format(out))
        else:
            print(u'\nPLATFORM TYPE\t\t\t=\tNot Virtual \N{BALLOT X}')
    def CHECK_VG(self,host,cmd1):
        #CHECK THE VOLUME GROUP EXISTS OR NOT
        # host = str(host)
        # cred = '{}@{}'.format(USER,host)
        host = host.rstrip()
        cmd2 = 'sudo vgdisplay | grep {}' .format(opts.vgname)
        cmd = ['ssh', '-t', '{}' .format(cmd1), "{}" .format(cmd2)]
        p1 = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p1.communicate()[0]
        out = p1.returncode
        if out != 0:
            print(u"\nVOLUME GROUP\t\t\t=\t{} \N{BALLOT X}" .format(opts.vgname))
        else:
            print(u"\nVOLUME GROUP\t\t\t=\t%s \N{check mark}" %opts.vgname)
    def CHECK_LV(self,host,cmd1):
        host = host.rstrip()
        cmd2 = 'sudo lvdisplay /dev/{}/{}' .format(opts.vgname, opts.lvname)
        cmd = ['ssh', '-t', '{}' .format(cmd1), "{}" .format(cmd2)]
        p1 = subprocess.Popen(cmd, shell=False, stdout=FNULL, stderr=subprocess.STDOUT)
        p1.communicate()[0]
        out = p1.returncode
        if out != 0:
            print(u"\nLOGICAL VOLUME\t\t\t=\t/dev/{}/{} \N{BALLOT X}" .format(opts.vgname,opts.lvname))
        else:
            print(u"\nLOGICAL VOLUME\t\t\t=\t/dev/{}/{} \N{check mark}" .format(opts.vgname,opts.lvname))
    def CHECK_FS_TYPE(self):
        if opts.fstype in ['ext3', 'ext4', 'xfs']:
            print(u"\nFILESYSTEM TYPE\t\t\t=\t{} \N{check mark}" .format(opts.fstype))
        else:
            print(u"\nFILESYSTEM TYPE\t\t\t=\t{} \N{BALLOT X}" .format(opts.fstype))
    def CONFIRM(self):
        #USER CONFIRMATION CHECK
        inp = input("Do you want to proceed? [Y/n] ")
        if inp != 'Y' and inp != 'y':
            exit(-1)
    def DISPLAY_INFO(self,host):
        #print('FILESYSTEM TYPE\t\t\t=\t{}' %(opts.fstype))
        pass
#MAIN Funtion
def main(host):
    x = EXTEND(opts.vgname,opts.lvname,opts.fstype,host)
    if opts.file == None:
        #PRE-CHECKS
        x.CHECK_PLATFORM(host)
        #x.CHECK_VG()
        #x.CHECK_LV()
        #DISPALY PROVIDED INFORMATION
        x.DISPLAY_INFO(host)
        #USER CONFIRMATION CHECK
        #CONFIRM()
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
            x.CHECK_VG(i,cmd1)
            x.CHECK_LV(i,cmd1)
            x.CHECK_FS_TYPE()
            #x.DISPLAY_INFO(i)
#MAIN
if __name__ == '__main__':
    if opts.vgname == None or opts.lvname == None or opts.fstype == None:
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