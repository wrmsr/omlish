"""
zha-quirks
"""
import asyncio
import glob
import functools
import math
import typing as ta

import bellows.config
import bellows.ezsp
import bellows.types
import bellows.zigbee.application
import zigpy.application
import zigpy.config
import zigpy.state
import zigpy.types
import zigpy.zdo


class App(zigpy.application.ControllerApplication):

    async def shutdown(self):
        pass

    async def startup(self, auto_form=False):
        pass

    async def request(
            self,
            device,
            profile,
            cluster,
            src_ep,
            dst_ep,
            sequence,
            data,
            expect_reply=True,
            use_ieee=False,
    ):
        pass

    async def permit_ncp(self, time_s=60):
        pass

    async def probe(self, config):
        return True


async def setup(dev, baudrate, cbh=None, configure=True):
    device_config = {
        bellows.config.CONF_DEVICE_PATH: dev,
        bellows.config.CONF_DEVICE_BAUDRATE: baudrate,
        bellows.config.CONF_FLOW_CONTROL: bellows.config.CONF_FLOW_CONTROL_DEFAULT,
    }
    s = bellows.ezsp.EZSP(device_config)
    if cbh:
        s.add_callback(cbh)
    await s.connect()
    await s.reset()
    await s.version()

    def check(ret, message, expected=0):
        if ret == expected:
            return
        if isinstance(expected, list) and ret in expected:
            return
        raise Exception(message)

    async def cfg(config_id, value):
        v = await s.setConfigurationValue(config_id, value)
        check(v[0], "Setting config %s to %s: %s" % (config_id, value, v[0]))

    c = s.types.EzspConfigId

    if configure:
        await cfg(c.CONFIG_STACK_PROFILE, 2)
        await cfg(c.CONFIG_SECURITY_LEVEL, 5)
        await cfg(c.CONFIG_SUPPORTED_NETWORKS, 1)
        await cfg(c.CONFIG_PACKET_BUFFER_COUNT, 64)

    return s


async def setup_application(app_config, startup=True):
    app_config = bellows.zigbee.application.ControllerApplication.SCHEMA(app_config)
    app = await bellows.zigbee.application.ControllerApplication.new(
        app_config, start_radio=startup
    )
    return app


def app(f, app_startup=True, extra_config=None):
    database_file = None
    application = None

    async def async_inner(ctx, *args, **kwargs):
        nonlocal database_file
        nonlocal application
        app_config = {
            bellows.config.CONF_DEVICE: {
                bellows.config.CONF_DEVICE_PATH: ctx.obj[bellows.config.CONF_DEVICE],
                bellows.config.CONF_DEVICE_BAUDRATE: ctx.obj[bellows.config.CONF_DEVICE_BAUDRATE],
                bellows.config.CONF_FLOW_CONTROL: ctx.obj[bellows.config.CONF_FLOW_CONTROL],
            },
            zigpy.config.CONF_DATABASE: ctx.obj["database_file"],
        }
        if extra_config:
            app_config.update(extra_config)
        application = await setup_application(app_config, startup=app_startup)
        ctx.obj["app"] = application
        await f(ctx, *args, **kwargs)
        await asyncio.sleep(0.5)
        await application.shutdown()

    def shutdown():
        try:
            application._ezsp.close()
        except:  # noqa: E722
            pass

    @functools.wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(async_inner(*args, **kwargs))
        except:  # noqa: E722
            # It seems that often errors like a message send will try to send
            # two messages, and not reading all of them will leave the NCP in
            # a bad state. This seems to mitigate this somewhat. Better way?
            loop.run_until_complete(asyncio.sleep(0.5))
            raise
        finally:
            shutdown()

    return inner


async def _async_main():
    def find_cu(suf: str) -> ta.Sequence[str]:
        return list(glob.glob(f'/dev/cu.GoControl_{suf}*'))

    device = next(iter(find_cu('zigbee')))

    config = App.SCHEMA(
        {
            zigpy.config.CONF_DATABASE: None,
            zigpy.config.CONF_DEVICE: {
                zigpy.config.CONF_DEVICE_PATH: "/dev/null",
            },
        },
    )

    # app = App(config)
    #
    # NCP_IEEE = zigpy.types.EUI64.convert("aa:11:22:bb:33:44:be:ef")
    #
    # app.state.node_information = zigpy.state.NodeInfo(
    #     zigpy.types.NWK(0x0000),
    #     ieee=NCP_IEEE,
    #     logical_type=zigpy.zdo.types.LogicalType.Coordinator,
    # )
    #
    # await dev.initialize()

    def channel_mask(channels):
        mask = 0
        for channel in channels:
            if not (11 <= channel <= 26):
                raise ValueError("channels must be from 11 to 26")
            mask |= 1 << channel
        return mask

    baudrate = 57600
    s = await setup(device, baudrate)

    channels = list(range(11, 27))
    channel_mask = channel_mask(channels)
    print("Scanning channels %s" % (" ".join(map(str, channels)),))

    duration_ms = 50
    # TFM says:
    #   Sets the exponent of the number of scan periods, where a scan period is
    #   960 symbols. The scan will occur for ((2^duration) + 1) scan periods.
    # 1 symbol is 16us
    duration_symbols = duration_ms / (960 * 0.016)
    duration_symbol_exp = max(0, math.ceil(math.log(duration_symbols - 1, 2)))

    energy_scan = False
    scan_type = bellows.types.EzspNetworkScanType.ACTIVE_SCAN
    if energy_scan:
        scan_type = bellows.types.EzspNetworkScanType.ENERGY_SCAN

    v = await s.startScan(scan_type, channel_mask, duration_symbol_exp)
    for network in v:
        print(network)

    s.close()


def _main():
    asyncio.run(_async_main())


if __name__ == '__main__':
    _main()
