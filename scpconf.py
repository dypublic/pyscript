#!/usr/bin/env python
import pty, re, os, stat, sys


class SSHError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SSH: 
    def __init__(self, ip, passwd, user, port):
        self.ip = ip
        self.passwd = passwd
        self.user = user
        self.port = port

    def run_cmd(self, c):
        (pid, f) = pty.fork()
        if pid == 0:
            os.execlp("ssh", "ssh", '-p %d' % self.port,
                      self.user + '@' + self.ip, c)
        else:
            return (pid, f)
    def push_file(self, src, dst):
        (pid, f) = pty.fork()
        if pid == 0:
            os.execlp("scp", "scp", '-P %d' % self.port,
                      src, self.user + '@' + self.ip + ':' + dst)
        else:
            return (pid, f) 

    def push_dir(self, src, dst):
        (pid, f) = pty.fork()
        if pid == 0:
            os.execlp("scp", "scp", '-P %d' % self.port, "-r", src,
                      self.user + '@' + self.ip + ':' + dst)
        else:
            return (pid, f)

    def _read(self, f):
        x = ''
        try:
            x = os.read(f, 1024)
        except Exception, e:
            # this always fails with io error
            pass
        return x

    def ssh_results(self, pid, f):
        output = ""
        got = self._read(f)         # check for authenticity of host request
        m = re.search("authenticity of host", got)
        if m:
            os.write(f, 'yes\n') 
            # Read until we get ack
            while True:
                got = self._read(f)
                m = re.search("Permanently added", got)
                if m:
                    break

            got = self._read(f)         # check for passwd request
        m = re.search("assword:", got)
        if m:
            # send passwd
            os.write(f, self.passwd + '\n')
            # read two lines
            tmp = self._read(f)
            tmp += self._read(f)
            m = re.search("Permission denied", tmp)
            if m:
                raise Exception("Invalid passwd")
            # passwd was accepted
            got = tmp
        else:
            raise Exception(got)
        while got and len(got) > 0:
            output += got
            got = self._read(f)
        os.waitpid(pid, 0)
        os.close(f)
        return output

    def cmd(self, c):
        (pid, f) = self.run_cmd(c)
        return self.ssh_results(pid, f)

    def push(self, src, dst):
        s = os.stat(src)
        if stat.S_ISDIR(s[stat.ST_MODE]):
            (pid, f) = self.push_dir(src, dst)
        else:
            (pid, f) = self.push_file(src, dst)
        return self.ssh_results(pid, f)

def ssh_cmd(ip, passwd, cmd, user, port=22):
    s = SSH(ip, passwd, user, port)
    return s.cmd(cmd)

def ssh_push(ip, passwd, src, dst, user, port=22): 
    s = SSH(ip, passwd, user, port)
    return s.push(src, dst)

if __name__ == '__main__':
    config_name = "scpconf_config.txt"
    boardip = '192.168.1.101'
    passwd = 'root'
    filepath = os.path.realpath(sys.argv[0])
    filedir = os.path.dirname(filepath)
    #print filedir
    config_path = os.path.join(filedir, config_name)
    try:
        f = open(config_path)
        ip_end = f.readline()
        if int(ip_end) < 255:
            boardip = boardip.rsplit('.', 1)[0] + '.' + ip_end
    except Exception, e: 
        print e

    print("default ip " + boardip)
    while 1:
        inputstr = raw_input("1:configuration file\n2:program\n3:change ip end\n->")
        if inputstr == '3':
            inputstr = raw_input("192.168.1.")
            boardip = '192.168.1.' + inputstr
            print "set ip to "+ boardip
            try:
                f = open(config_path,"w")
                f.write(inputstr)
            except Exception as e:
                print e
        else:
            break
    
    allpath = {
               '1':[[r'/home/daiyue/TSS/Software/testDB/*.db',
                     r"/honeywell/runtime"],
                    [r'/home/daiyue/TSS/Software/GCPSWExt/APPFW/IDE/VS2008/USPROTO_APPFW_WINDOWS_VS2008/configuration.xml',
                     r'/honeywell/runtime/configuration.xml']],
               '2':[[r'/home/daiyue/TSS/Software/GCPSWExt/Main/TSS_LINUX_TIMESYS_CROSS_DEBUG/TSS_Main_stripped',
                     r'/honeywell']]
               }
    try:
        paths = allpath[inputstr]
    except:
        print "not have this number\n"
        exit()
    for path in paths:
        if '*' in path[0]:
            pathhead , _ = os.path.split(path[0])
            files = os.listdir(pathhead)
            files = [r'%s/%s'%(pathhead,file) for file in files if file.endswith('.db')]
        else:
            files = [path[0]]
        for file in files:
            print file
            ssh_push(boardip, passwd,file,path[1],'root')


