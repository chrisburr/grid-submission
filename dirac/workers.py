import json
import os
import shutil

import gevent

from . import applications
from . import db
from . import dirac
from . import WORKDIR


submitting_queue = gevent.queue.Queue()
monitoring_queue = gevent.queue.Queue()
downloading_queue = gevent.queue.Queue()


def submit_worker():
    while True:
        j = submitting_queue.get()
        print('Submitting job')
        dirac_job = j._as_dirac_job() if isinstance(j, applications.Job) else j
        response = dirac.submit(dirac_job)

        jid = response['JobID']

        obj = {'jid': jid,
               'status': 'Submitted',
               'downloaded': False,
               'download_retries': 1}

        db.Put(bytes(jid), json.dumps(obj))
        monitoring_queue.put(obj)
        print('Submitted job')


def monitor_worker():
    while True:
        obj = monitoring_queue.get()
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
            downloading_queue.put(obj)
        else:
            obj['status'] = new_status
            if new_status != status:
                db.Put(bytes(jid), json.dumps(obj))
                print('Job {} changed to {}'.format(jid, new_status))
            monitoring_queue.put(obj)


def download_worker():
    done_folder = os.path.join(WORKDIR, 'succeeded')
    failed_folder = os.path.join(WORKDIR, 'failed')
    while True:
        obj = downloading_queue.get()
        jid = obj['jid']
        print('Downloading job {}'.format(jid))
        try:
            output_folder = dirac.get_job_output(jid, WORKDIR)
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
                downloading_queue.put(obj)
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


def start_workers(join=False):
    submitting_group = gevent.pool.Group()
    monitoring_group = gevent.pool.Group()
    downloading_group = gevent.pool.Group()

    for i in range(10):
        submitting_group.spawn(submit_worker)

    for i in range(10):
        monitoring_group.spawn(monitor_worker)

    for i in range(10):
        downloading_group.spawn(download_worker)

    for k, v in db.RangeIter():
        obj = json.loads(v)
        if not obj['downloaded']:
            monitoring_queue.put(obj)

    submitting_group.join()
    monitoring_group.join()
    downloading_group.join()


def submit(j):
    submitting_queue.put(j)
