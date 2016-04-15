#!/usr/bin/env python2
from __future__ import print_function

import argparse


def submit_command(args):
    from dirac import applications, submit, GridFile

    SUBMISSION_ENVIRONMENT = {
        'Job': applications.Job,
        'GridFile': GridFile,
        'GaussJob': applications.GaussJob,
        'BooleJob': applications.BooleJob,
        'MooreJob': applications.MooreJob,
        'BrunelJob': applications.BrunelJob,
        'GaudiJob': applications.GaudiJob,
        'DaVinciJob': applications.DaVinciJob,
        'submit': submit
    }

    with open(args.submission_script) as f:
        code = compile(f.read(), args.submission_script, 'exec')
        exec(code, SUBMISSION_ENVIRONMENT, {})


def watch_command(args):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LHC grid submission tool')
    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        help='additional help'
    )

    submit_parser = subparsers.add_parser('submit')
    submit_parser.add_argument('submission_script')
    submit_parser.set_defaults(func=submit_command)

    watch_parser = subparsers.add_parser('watch')
    watch_parser.set_defaults(func=watch_command)

    args = parser.parse_args()
    args.func(args)

    import dirac
    dirac.start_ui()
    dirac.start_workers()
