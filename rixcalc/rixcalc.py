from caproto import ChannelData, ChannelType
from caproto.server import AsyncLibraryLayer, PVGroup, pvproperty
from caproto.sync.client import read
from .chemrixs import get_KBs, get_E, get_benders
from .mono_calc import get_lin_disp


class Rixcalc(PVGroup):


    """
    General Purpose IOC for using python to calculate and build various PVs.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Init here

    tar_mono_energy = pvproperty(
        value=0.0,
        name='TAR_MONO_E',
        record='ai',
        read_only=True,
        units='eV',
        doc='Current Target Mono Energy',
        precision=3,
    )

    mono_e = pvproperty(
        value=0.0,
        name='MONO_E',
        record='ai',
        read_only=True,
        units='eV',
        doc='Current Mono Energy',
        precision=3,
    )

    fel_e = pvproperty(
        value=0.0,
        name='FEL_E',
        record='ai',
        read_only=True,
        units='eV',
        doc='FEL Set Energy',
        precision=3,
    )


    mr1k1_focus = pvproperty(
        value=0.0,
        name='MR1K1_FOCUS',
        record='ai',
        read_only=True,
        units='m',
        doc='MR1K1 Focus',
        precision=3,
    )

    mr3k2_focus = pvproperty(
        value=0.0,
        name='MR3K2_FOCUS',
        record='ai',
        read_only=True,
        units='m',
        doc='MR3K2 (Horizontal) Focus',
        precision=3,
    )

    mr4k2_focus = pvproperty(
        value=0.0,
        name='MR4K2_FOCUS',
        record='ai',
        read_only=True,
        units='m',
        doc='MR4K2 (Vertical) Focus',
        precision=3,
    )

    lin_disp = pvproperty(
        value=0.0,
        name='LIN_DISP',
        record='ai',
        read_only=True,
        units='meV/um',
        doc='Reciprocal Linear Dispersion',
        precision=3,
    )


    @tar_mono_energy.scan(period=1.0, stop_on_error=False, use_scan_field=True)
    async def tar_mono_energy(self, instance: ChannelData, async_lib: AsyncLibraryLayer):
        """
        Scan hook for scanned.

        This updates at a rate of 10Hz, unless the user changes .SCAN.
        """

        target_mono_energy, current_mono_energy, fel_set = get_E()
        mr1k1 = get_benders()
        mr3k2_h_1, mr3k2_h_2, mr4k2_v_1, mr4k2_v_2 = get_KBs()
        linear_dispersion = get_lin_disp()

        await self.tar_mono_energy.write(value = target_mono_energy)
        await self.mono_e.write(value = current_mono_energy)
        await self.fel_e.write(value = fel_set)
        await self.mr1k1_focus.write(value = mr1k1)
        await self.mr3k2_focus.write(value = mr3k2_h_2)
        await self.mr4k2_focus.write(value = mr4k2_v_2)
        await self.lin_disp.write(value = linear_dispersion)
