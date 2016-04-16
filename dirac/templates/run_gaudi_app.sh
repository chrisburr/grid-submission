#!/usr/bin/env bash
set -e
source /cvmfs/lhcb.cern.ch/lib/LbLogin.sh
set -x
set -u

tar -czf boole_sandbox.tar.gz *
lb-run {app_name} {version} gaudirun.py {options} || true
