from typing import Optional

from ophyd import EpicsSignalRO
from .chemrixs import get_KBs, get_E, get_benders
from .mono_calc import get_lin_disp
from caproto.server import PVGroup, ioc_arg_parser, pvproperty, run

class PvSubscribeHelper:
    # These are type hints that tell our IDE that this class has a "mr1k1_bend_us_pos"
    # attribute that should be a float but sometimes might be uninitialized -
    # or None
    mr1k1_bend_us_pos: Optional[float]
    mr1k1_bend_ds_pos: Optional[float]
    mr3k2_kbh_us_pos: Optional[float]
    mr3k2_kbh_ds_pos: Optional[float]
    mr4k2_kbh_us_pos: Optional[float]
    mr4k2_kbh_ds_pos: Optional[float]
    mono_gpi_rbv: Optional[float]
    mono_gpi_sp: Optional[float]
    mono_mpi_rbv: Optional[float]
    mono_mpi_sp: Optional[float]
    mono_e: Optional[float]


    # Let's keep track of the signals we have. Let's map each signal
    # onto an attribute.
    signals: dict[EpicsSignalRO, str]

    def __init__(self):
        # On initialization, we don't have values just yet!
        self.mr1k1_bend_us_pos = None
        self.mr1k1_bend_ds_pos = None
        self.mr3k2_kbh_us_pos = None
        self.mr3k2_kbh_ds_pos = None
        self.mr4k2_kbh_us_pos = None
        self.mr4k2_kbh_ds_pos = None
        self.mono_gpi_rbv = None
        self.mono_gpi_sp = None
        self.mono_mpi_rbv = None
        self.mono_mpi_sp = None
        self.mono_e = None

        self.subscribe()

    def subscribe(self):
        self.signals = {
            EpicsSignalRO("MR1K1:BEND:MMS:US.RBV"): "mr1k1_bend_us_pos",
            EpicsSignalRO("MR1K1:BEND:MMS:DS.RBV"): "mr1k1_bend_ds_pos",
            EpicsSignalRO("MR3K2:KBH:MMS:BEND:US.RBV"): "mr3k2_kbh_us_pos",
            EpicsSignalRO("MR3K2:KBH:MMS:BEND:DS.RBV"): "mr3k2_kbh_ds_pos",
            EpicsSignalRO("MR4K2:KBV:MMS:BEND:US.RBV"): "mr4k2_kbh_us_pos",
            EpicsSignalRO("MR4K2:KBV:MMS:BEND:DS.RBV"): "mr4k2_kbh_ds_pos",
            EpicsSignalRO("SP1K1:MONO:MMS:G_PI.RBV"): "mono_gpi_rbv",
            EpicsSignalRO("SP1K1:MONO:MMS:G_PI"): "mono_gpi_sp",
            EpicsSignalRO("SP1K1:MONO:MMS:M_PI.RBV"): "mono_mpi_rbv",
            EpicsSignalRO("SP1K1:MONO:MMS:M_PI"): "mono_mpi_sp",
            EpicsSignalRO("SP1K1:MONO:CALC:ENERGY"): "mono_e",
        }

        for sig in self.signals:
            sig.subscribe(self.value_update_callback)

    def value_update_callback(self, value, obj: EpicsSignalRO, **kwargs):
        attribute_name = self.signals[obj]
        setattr(self, attribute_name, value)



class Rixcalc(PVGroup):


    """
    General Purpose IOC for using python to calculate and build various PVs.
    """

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

    calc_update = pvproperty(
        value=True,
        record="bo",
        name="CalcUpdate",
        doc="Calculation helper - periodically update calculation data"
    )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Init here

        self.pv_subscribe_helper = PvSubscribeHelper()

    @calc_update.scan(period=1.0, use_scan_field=True)
    async def calc_update(self, instance, async_lib):
        helper = self.pv_subscribe_helper
        if all(x is not None for x in (helper.mr1k1_bend_us_pos, helper.mr1k1_bend_ds_pos, helper.mr3k2_kbh_us_pos, helper.mr3k2_kbh_ds_pos, helper.mr4k2_kbh_us_pos, helper.mr4k2_kbh_ds_pos)) :
            mr1k1 = get_benders(helper.mr1k1_bend_us_pos, helper.mr1k1_bend_ds_pos)
            mr3k2_h_1, mr3k2_h_2, mr4k2_v_1, mr4k2_v_2 = get_KBs(helper.mr3k2_kbh_us_pos, helper.mr3k2_kbh_ds_pos, helper.mr4k2_kbh_us_pos, helper.mr4k2_kbh_ds_pos)
 
            await self.mr1k1_focus.write(mr1k1)
            await self.mr3k2_focus.write(mr3k2_h_2)
            await self.mr4k2_focus.write(mr4k2_v_2)

        if all(x is not None for x in (helper.mono_gpi_rbv, helper.mono_gpi_sp, helper.mono_mpi_rbv, helper.mono_mpi_sp, helper.mono_e)):
            current_mono_energy, target_mono_energy = get_E(helper.mono_gpi_rbv, helper.mono_gpi_sp, helper.mono_mpi_rbv, helper.mono_mpi_sp)
            linear_dispersion = get_lin_disp(helper.mono_e)

            await self.mono_e.write(current_mono_energy)
            await self.tar_mono_energy.write(target_mono_energy)
            await self.lin_disp.write(linear_dispersion)
