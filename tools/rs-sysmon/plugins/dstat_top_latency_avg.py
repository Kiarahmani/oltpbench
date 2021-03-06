### Dstat most expensive I/O process plugin
### Displays the name of the most expensive I/O process
###
### Authority: dag@wieers.com

### For more information, see:
###     http://eaglet.rain.com/rick/linux/schedstat/

class dstat_plugin(dstat):
    def __init__(self):
        self.name = 'highest average'
        self.vars = ('latency process',)
        self.type = 's'
        self.width = 17
        self.scale = 0
        self.pidset1 = {}; self.pidset2 = {}

    def check(self):
        if not os.access('/proc/self/schedstat', os.R_OK):
            raise Exception, 'Kernel has no scheduler statistics, use at least 2.6.12'

    def extract(self):
        self.val['result'] = 0
        self.val['latency process'] = ''
        for pid in proc_pidlist():
            try:
                ### Reset values
                if not self.pidset1.has_key(pid):
                    self.pidset1[pid] = {'wait_ticks': 0, 'ran': 0}

                ### Extract name
                name = proc_splitline('/proc/%s/stat' % pid)[1][1:-1]

                ### Extract counters
                l = proc_splitline('/proc/%s/schedstat' % pid)
            except IOError:
                continue
            except IndexError:
                continue

            if len(l) != 3: continue

            self.pidset2[pid] = {'wait_ticks': long(l[1]), 'ran': long(l[2])}

            if self.pidset2[pid]['ran'] - self.pidset1[pid]['ran'] > 0:
                avgwait = (self.pidset2[pid]['wait_ticks'] - self.pidset1[pid]['wait_ticks']) * 1.0 / (self.pidset2[pid]['ran'] - self.pidset1[pid]['ran']) / elapsed
            else:
                avgwait = 0

            ### Get the process that spends the most jiffies
            if avgwait > self.val['result']:
                self.val['result'] = avgwait
                self.val['pid'] = pid
                self.val['name'] = getnamebypid(pid, name)

        if step == op.delay:
            for pid in self.pidset2.keys():
                self.pidset1[pid].update(self.pidset2[pid])

        if self.val['result'] != 0.0:
            self.val['latency process'] = '%-*s%s' % (self.width-4, self.val['name'][0:self.width-4], cprint(self.val['result'], 'f', 4, 100))

        ### Debug (show PID)
#       self.val['latency process'] = '%*s %-*s' % (5, self.val['pid'], self.width-6, self.val['name'])

    def showcsv(self):
        return '%s / %.4f' % (self.val['name'], self.val['result'])

# vim:ts=4:sw=4:et
