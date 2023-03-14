from typing import Optional

from ophyd import EpicsSignalRO
from .chemrixs import get_KBs, get_E, get_benders
from .mono_calc import get_lin_disp
from caproto.server import PVGroup, ioc_arg_parser, pvproperty, run

class PvSubscribeHelper:
    # These are type hints that tell our IDE that this class has a "value1"
    # attribute that should be a float but sometimes might be uninitialized -
    # or None
    value1: Optional[float]
    value2: Optional[float]
    value3: Optional[float]
    value4: Optional[float]
    value5: Optional[float]
    value6: Optional[float]
    value7: Optional[float]
    value8: Optional[float]
    value9: Optional[float]
    value10: Optional[float]
    value11: Optional[float]


    # Let's keep track of the signals we have. Let's map each signal
    # onto an attribute.
    signals: dict[EpicsSignalRO, str]

    def __init__(self):
        # On initialization, we don't have values just yet!
        self.value1 = None
        self.value2 = None
        self.value3 = None
        self.value4 = None
        self.value5 = None
        self.value6 = None
        self.value7 = None
        self.value8 = None
        self.value9 = None
        self.value10 = None
        self.value11 = None

        self.subscribe()

    def subscribe(self):
        self.signals = {
            EpicsSignalRO("MR1K1:BEND:MMS:US"): "value1",
            EpicsSignalRO("MR1K1:BEND:MMS:DS"): "value2",
            EpicsSignalRO("MR3K2:KBH:MMS:BEND:US"): "value3",
            EpicsSignalRO("MR3K2:KBH:MMS:BEND:DS"): "value4",
            EpicsSignalRO("MR4K2:KBV:MMS:BEND:US"): "value5",
            EpicsSignalRO("MR4K2:KBV:MMS:BEND:DS"): "value6",
            EpicsSignalRO("SP1K1:MONO:MMS:G_PI.RBV"): "value7",
            EpicsSignalRO("SP1K1:MONO:MMS:G_PI"): "value8",
            EpicsSignalRO("SP1K1:MONO:MMS:M_PI.RBV"): "value9",
            EpicsSignalRO("SP1K1:MONO:MMS:M_PI"): "value10",
            EpicsSignalRO("SP1K1:MONO:CALC:ENERGY"): "value11",
        }

        for sig in self.signals:
            sig.subscribe(self.value_update_callback)

    def value_update_callback(self, value, obj: EpicsSignalRO, **kwargs):
        print("A value updated from", obj)
        print("The new value is", value)

        attribute_name = self.signals[obj]
        print("This should go to the", attribute_name, "attribute")
        setattr(self, attribute_name, value)
        print("Updated", attribute_name, "to", getattr(self, attribute_name))



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
        if not [x for x in (helper.value1, helper.value2, helper.value3, helper.value4, helper.value5, helper.value6) if x is None]:
            mr1k1 = get_benders(helper.value1, helper.value2)
            mr3k2_h_1, mr3k2_h_2, mr4k2_v_1, mr4k2_v_2 = get_KBs(helper.value3, helper.value4, helper.value5, helper.value6)
 
            await self.mr1k1_focus.write(mr1k1)
            await self.mr3k2_focus.write(mr3k2_h_2)
            await self.mr4k2_focus.write(mr4k2_v_2)

        if not [x for x in (helper.value7, helper.value8, helper.value9, helper.value10, helper.value11) if x is None]:
            current_mono_energy, target_mono_energy = get_E(helper.value7, helper.value8, helper.value9, helper.value10)
            linear_dispersion = get_lin_disp(helper.value11)

            await self.mono_e.write(current_mono_energy)
            await self.tar_mono_energy.write(target_mono_energy)
            await self.lin_disp.write(linear_dispersion)
