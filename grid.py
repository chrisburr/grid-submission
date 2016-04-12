#!/usr/bin/env python2

from __future__ import print_function

import gevent
import gevent.queue
import gevent.pool
import gevent.subprocess
import gevent.monkey

gevent.monkey.patch_all()

from functools import partial

from DIRAC import S_OK, S_ERROR, gLogger, exit
from DIRAC.Core.Base import Script
Script.parseCommandLine(ignoreErrors = False)
from DIRAC.Interfaces.API.Job import Job
from DIRAC.Interfaces.API.Dirac import Dirac

import argparse
import json
import collections
import shutil
import os
WORKDIR = os.getcwd()
import leveldb
db = leveldb.LevelDB(os.path.join(WORKDIR, 'jobs.db'))

from dirac import bk_query, split_input_data, get_job_output

submitting_group = gevent.pool.Group()
submitting = gevent.queue.Queue()
monitoring_group = gevent.pool.Group()
monitoring = gevent.queue.Queue()
downloading_group = gevent.pool.Group()
downloading = gevent.queue.Queue()

def submit_():
    while True:
        j = submitting.get()
        print('Submitting job')
        resp = dirac.submit(j)
        jid = resp['JobID']

        obj = {'jid': jid,
               'status': 'Submitted',
               'downloaded': False,
               'download_retries': 1}

        db.Put(bytes(jid), json.dumps(obj))
        monitoring.put(obj)
        print('Submitted job')

def monitor_():
    while True:
        obj = monitoring.get()
        jid = obj['jid']
        status = obj['status']
        resp = dirac.status(jid)
        new_status = resp['Value'][jid]['Status']
        if new_status == 'Done' or new_status == 'Failed':
            if new_status == 'Done':
                print('Job {} finished!'.format(jid))
            else:
                print('Job {} failed!'.format(jid))
            obj['status'] = new_status
            db.Put(bytes(jid), json.dumps(obj))
            downloading.put(obj)
        else:
            obj['status'] = new_status
            if new_status != status:
                db.Put(bytes(jid), json.dumps(obj))
                print('Job {} changed to {}'.format(jid, new_status))
            monitoring.put(obj)

def download_():
    done_folder = os.path.join(WORKDIR, 'succeeded')
    failed_folder = os.path.join(WORKDIR, 'failed')
    while True:
        obj = downloading.get()
        jid = obj['jid']
        print('Downloading job {}'.format(jid))
        try:
            output_folder = get_job_output(jid, WORKDIR)
            if obj['status'] == 'Done':
                if not os.path.exists(done_folder):
                    os.mkdir(done_folder)
                shutil.move(output_folder,
                            os.path.join(done_folder, str(jid)))
            elif obj['status'] == 'Failed':
                if not os.path.exists(failed_folder):
                    os.mkdir(failed_folder)
                shutil.move(output_folder,
                            os.path.join(failed_folder, str(jid)))
            else:
                raise ValueError('Unfinished job pushed to Download queue')
            obj['downloaded'] = True
            print('Downloaded job {}'.format(jid))
        except:
            print('Could not download output of job {}'.format(jid))
            if obj['download_retries'] > 0:
                obj['download_retries'] -= 1
                downloading.put(obj)
                print('Retrying download of job {} later'.format(jid))
            else:
                obj['status'] = 'Failed'
                if not os.path.exists(failed_folder):
                    os.mkdir(failed_folder)
                if os.path.exists(os.path.join(WORKDIR, str(jid))):
                    shutil.move(os.path.join(WORKDIR, str(jid)),
                                os.path.join(failed_folder, str(jid)))
                obj['downloaded'] = False
        db.Put(bytes(jid), json.dumps(obj))

# To be called by the submission script
def submit(j):
    submitting.put(j)

def submit_command(args):
    execfile(args.submission_script)

def watch_command(args):
    pass

def print_summary():
    counter = collections.Counter()
    for k, v in db.RangeIter():
        obj = json.loads(v)
        counter[obj['status']] += 1
    display = [
               ('S', 'Submitted'),
               ('R', 'Received'),
               ('W', 'Waiting'),
               ('M', 'Matched'),
               ('R', 'Running'),
               ('D', 'Done'),
               ('F', 'Failed'),
              ]
    output = []
    for d in display:
        output.append('{}: {: 3d}'.format(d[0], counter[d[1]]))
    print('\t'.join(output))
    gevent.sleep(5)
    gevent.spawn(print_summary)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='LHC grid submission tool')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='additional help')
    submit_parser = subparsers.add_parser('submit')
    submit_parser.add_argument('submission_script')
    submit_parser.set_defaults(func=submit_command)
    watch_parser = subparsers.add_parser('watch')
    watch_parser.set_defaults(func=watch_command)

    args = parser.parse_args()

    dirac = Dirac()

    tasks = []

    args.func(args)

    gevent.spawn(print_summary)

    for i in range(10):
        submitting_group.spawn(submit_)

    for i in range(10):
        monitoring_group.spawn(monitor_)

    for i in range(10):
        downloading_group.spawn(download_)

    for k, v in db.RangeIter():
        obj = json.loads(v)
        if not obj['downloaded']:
            monitoring.put(obj)

    gevent.joinall(tasks)
    submitting_group.join()
    monitoring_group.join()
    downloading_group.join()
