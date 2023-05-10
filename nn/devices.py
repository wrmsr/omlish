from omlish import lang


class Device(lang.Abstract):
    pass


class CpuDevice(Device):
    pass


DEFAULT_DEVICE: Device = CpuDevice()
