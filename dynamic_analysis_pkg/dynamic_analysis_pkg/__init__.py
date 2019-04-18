
from os import makedirs
from os.path import join, exists, isdir, basename
import pyunicore.client as unicore_client


class Results:

    BASE = 'https://zam2125.zam.kfa-juelich.de:9112/NUVLA/rest/core'
    CIRCUIT_DIR = '/mnt/circuits/O1/20181114'
    DEFAULT_WD_BASE = '/home/jovyan/tmp/test_pull_unicore';
    job_base = join(BASE, 'jobs')
    files_list = None
    circuit_dir = None
    local_dir = None
    blueconfig = None

    def __init__(self, token, sim_id, base_working_directory=None):
        if base_working_directory == None:
            base_working_directory = self.DEFAULT_WD_BASE
        self.define_paths(base_working_directory, sim_id)
        self.fetch_results(token, sim_id)
        self.blueconfig = join(self.local_dir, 'BlueConfig')

    def fetch_results(self, token, sim_id=None):
        if not sim_id:
            print('[Error] Provide Simulation ID')
            return
        self.retrieve_sim_info(token, sim_id)
        self.get_sim_results()

    def retrieve_sim_info(self, token, sim_id=None):
        tr = unicore_client.Transport(token)
        job_url = join(self.job_base, sim_id)
        job = unicore_client.Job(tr, job_url)
        print('Fetching results of: {}'.format(job.properties['name']))
        storage = job.working_dir
        self.files_list = storage.listdir()

    def get_sim_results(self):
        self.download_blueconfig()
        self.download_report()
        self.download_out_dat()

    def define_paths(self, working_directory, sim_id):
        self.local_dir = join(working_directory, sim_id)
        if not exists(self.local_dir):
            makedirs(self.local_dir)

        if not isdir(self.CIRCUIT_DIR):
            circuit_directory = basename(self.CIRCUIT_DIR)
        else:
            circuit_directory = self.CIRCUIT_DIR
        self.circuit_dir = circuit_directory

    def download_file_to_storage(self, file_name):
        # function to download the file and add it to kernel file system
        x = self.files_list[file_name]
        file_content = x.raw().read()

        new_path = join(self.local_dir, file_name)

        if file_name == 'BlueConfig':
            writable_content = file_content.replace('/mooc', '/mnt')
            writable_content = writable_content.replace('/io',
                    self.local_dir)
        else:
            writable_content = file_content

        with open(new_path, 'w') as fd:
            fd.write(writable_content)

        print('- {} downloaded'.format(file_name))

    def download_blueconfig(self, file_name='BlueConfig'):
        self.download_file_to_storage(file_name)

    def download_report(self):
        # find report
        report = next((x for x in self.files_list if '_report_' in x), None)
        if not report:
            print('No reports were found')
            return
        self.download_file_to_storage(report)

    def download_out_dat(self):
        self.download_file_to_storage('out.dat')


class FetchMultipleResults:

    values = []

    def __init__(self, token, sim_list_ids, base_working_directory=None):

        total_sims = len(sim_list_ids)
        for idx, sim in enumerate(sim_list_ids):
            print('({}/{})'.format(idx + 1, total_sims))
            self.values.append(Results(token, sim, base_working_directory))
