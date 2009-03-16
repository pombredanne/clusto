
import re
from clusto.drivers.base import Location, Device, Driver

class BasicRack(Location):
    """
    Basic rack driver.
    """

    _clustoType = "rack"
    _driverName = "basicrack"

    _properties = {'minu':1,
                   'maxu':45}
    

    def _ensureRackU(self, rackU):
        if not isinstance(rackU, int) and not isinstance(rackU, (list, tuple)):
            raise TypeError("a rackU must be an Integer or list/tuple of Integers.")


        if isinstance(rackU, list):
            for U in rackU:
                if not isinstance(U, int):
                    raise TypeError("a rackU must be an Integer or List of Integers.")

        if isinstance(rackU, int):
            rackU = [rackU]
        else:
            rackU = list(rackU)

        # do U checks
        for U in rackU:
            if U > self.maxu:
                raise TypeError("the rackU must be less than %d." % self.maxu)
            if U < self.minu:
                raise TypeError("RackUs may not be negative.")

        rackU.sort()
        last = rackU[0]
        for i in rackU[1:]:
            if i == last:
                raise TypeError("you can't list the same U twice.")
            if (i-1) != (last):
                raise TypeError("a device can only occupy multiple Us if they're adjacent.")
            last = i

        return rackU

    def insert(self, device, rackU):
        """Insert a given device into the given rackU."""
    
        
        if not isinstance(device, Device):
            raise TypeError("You can only add Devices to a rack.  %s is a"
                            " %s" % (device.name, str(device.__class__)))

        rackU = self._ensureRackU(rackU)

        rau = self.getRackAndU(device)

        if rau != None:
            raise Exception("%s is already in rack %s"
                            % (device.name, rau['rack'].name))

        
        for U in rackU:
            dev = self.getDeviceIn(U)
            if dev:
                raise TypeError("%s is already in RU %d" % (dev.name, U))

        for U in rackU:
            self.addAttr("_contains", device, numbered=U, subkey='ru')

        
    def getDeviceIn(self, rackU):
        
        if not isinstance(rackU, int):
            raise TypeError("RackU must be a single integer. Got: %s" % str(rackU))

        rackU = self._ensureRackU(rackU)[0]
        
        owners = self.contents(numbered=rackU, subkey='ru')

        if len(owners) > 1:
            raise Exception('Somehow there is more than one thing in %s.'
                            'Only one of these should be in this space in the '
                            'rack: %s' % (self.ruName(rackU),
                                          ','.join([x.name for x in owners])))
        if owners:
            return owners[0]
        
        return None

    @classmethod
    def getRackAndU(cls, device):
        """
        Get the rack and rackU for a given device.

        returns a tuple of (rack, u-number)
        """

        rack = set(device.parents(clustoTypes=[cls]))


        if len(rack) > 1:
            raise Exception("%s is somehow in more than one rack, this will "
                            "likely need to be rectified manually.  It currently "
                            "appears to be in racks %s"
                            % (device.name, str(rack)))

        if rack:
            rack = rack.pop()
            return {'rack':Driver(rack.entity),  
                    'RU':[x.number for x in rack.contentAttrs(value=device,
                                                              subkey='ru')]}
        else:
            
            return None