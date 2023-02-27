import textwrap

import caproto.server

from .rixcalc import Rixcalc


def main():
    ioc_options, run_options = caproto.server.ioc_arg_parser(
        default_prefix='RIX:CALC:01:',
        desc=textwrap.dedent(Rixcalc.__doc__)
    )

    ioc = Rixcalc(**ioc_options)
    caproto.server.run(ioc.pvdb, **run_options)


if __name__ == '__main__':
    main()
