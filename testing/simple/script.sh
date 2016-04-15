#!/usr/bin/env bash

source /cvmfs/lhcb.cern.ch/lib/LbLogin.sh
ls
env
tar -czf simple_sandbox.tar.gz *
ls -ltrah
