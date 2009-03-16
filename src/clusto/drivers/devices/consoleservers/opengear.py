from basicconsoleserver import BasicConsoleServer
from clusto.exceptions import ConnectionException

from subprocess import Popen

class OpenGearCM4148(BasicConsoleServer):

    _driverName = 'opengearcm4148'

    _portmeta = { 'pwr-nema-5' : { 'numports':1, },
                  'nic-eth' : { 'numports':1, },
                  'console-serial' : { 'numports':48, },
                  }

    def connect(self, porttype, num, ssh_user):
        if porttype != 'console-serial':
            raise DriverException("Cannot connect to a non-serial port")

        proc = Popen(['ssh', '-p', str(num + 3000), '%s@%s' % (ssh_user, self.name)])
        proc.communicate()