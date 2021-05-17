import subprocess
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from mipqctool.controller import DockerDB
from mipqctool.config import LOGGER, MIPMAP_DB_PORT, MIPMAP_DB_PASSWORD, MIPMAP_DB_CONTAINER
from mipqctool.exceptions import DockerExecError

class DockerMipmap(object):    
    def __init__(self, mapping, source, target, output):
        """Class for executing the mapping task with docker container.
        Arguments:
        :param mapping: folderpath containing the mapping xml file
        :param source: folderpath with the source csv file
        :param target: folderpath with the target csv file
        :param output: folderpath where the output file will be saved
        """
        self.__image = 'hbpmip/mipmap'
        self.__name = 'mipmap'
        xmlpath = Path(mapping)
        self.__mappingpath = str(xmlpath.parent)
        self.__mapping = mapping
        self.__source = source
        self.__target = target
        self.__output = output

        # set the folder where the run.sh script is located
        lib_path = os.path.abspath(os.path.dirname(__file__))
        thispath = Path(lib_path)
        parentpath = str(thispath.parent)
        self.__scriptpath  = os.path.join(parentpath, 'data', 'mapping', 'script')

        # set the folder where the dbproperties file will be located
        self.__dbprop = os.path.join(self.__mappingpath, 'dbproperties')
        if not os.path.isdir(self.__dbprop):
            os.mkdir(self.__dbprop)
        
        # create the mipmap db container
        db = DockerDB(MIPMAP_DB_CONTAINER, MIPMAP_DB_PORT, MIPMAP_DB_PASSWORD)
        db.render_dbproperties(self.__dbprop)



        
        env_path = os.path.join(parentpath, 'data', 'templates')
        env = Environment(loader=FileSystemLoader(env_path))
        template_file = 'docker-compose.j2'
        self.__template = env.get_template(template_file)

        
        self.__dcompose = os.path.join(self.__mappingpath, 'docker-compose.yml')

        self.__run_mapping()

    def __run_mapping(self):
        env = {}
        env['mipmap_map'] = self.__mapping
        env['mipmap_source'] = self.__source
        env['mipmap_output'] = self.__output
        env['mipmap_pgproperties'] = self.__dbprop
        env['mipmap_script'] = self.__scriptpath
        env['mipmap_target'] = self.__target
        env['mipmap_db'] = MIPMAP_DB_CONTAINER
        #LOGGER.debug(os.getenv('mipmap_pgproperties'))
        self.__template.stream(env).dump(self.__dcompose)
        if self.__is_mipmap_container_exist:
            LOGGER.info('Removing previous mipmap container...')
            remove_proc = subprocess.run(['docker', 'rm', self.__name])

        arguments = ['docker-compose', '-f', self.__dcompose, 'up', 'mipmap_etl']

        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        LOGGER.info('Running docker-compose...')
        output, _ = process.communicate()
        LOGGER.info(output.decode('utf-8'))

        # except subprocess.CalledProcessError:
        #     LOGGER.warning('There was an error while attempting'
        #                    ' running the docker mapping container.')
        #     raise DockerExecError('There was an error while attempting'
        #                           ' running the docker mapping container.')

    def __is_mipmap_container_exist(self):

        proc_docker = subprocess.Popen(['docker', 'ps', '-a'],
                                       stdout=subprocess.PIPE)
        proc_grep = subprocess.Popen(['grep', self.__name],
                                       stdin=proc_docker.stdout,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        stdout, _ = proc_grep.communicate()
        output = str(stdout).split()
        LOGGER.debug(output)
        try:
            container_name = output[-1]
            # remove new line spacial character
            container_name = container_name.rstrip("\\n'")
        except IndexError:
            container_name = None
            
        if container_name == self.__name:
            return True
        else:
            return False
