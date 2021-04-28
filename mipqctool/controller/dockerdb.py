import subprocess

import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from mipqctool.config import LOGGER, MIPMAP_DB_NAME, MIPMAP_DB_USER
from mipqctool.exceptions import DockerExecError


class DockerDB(object):

    def __init__(self, name, port, password):
        """Class for creating and handling the database
        docker container for execution a mapping task. 
        Two containers are needed:
        1. postgres:9.6 
        Arguments:
        :param name: db container name
        :param port: the external port of the db container
        :param password: password for the postgres user
        """
        self.__db_image = 'postgres:9.6'
        self.__dbname = name
        self.__dbport = port
        self.__dbuser = MIPMAP_DB_USER
        self.__dbpassword = password
        self.__is_db_exist = False
        self.__is_db_running = False
        self.__mipmapname = MIPMAP_DB_NAME

        lib_path = os.path.abspath(os.path.dirname(__file__))
        thispath = Path(lib_path)
        parentpath = str(thispath.parent)
        env_path = os.path.join(parentpath, 'data', 'templates')
        env = Environment(loader=FileSystemLoader(env_path))
        template_file = 'mipmap-db.properties.j2'
        self.__template = env.get_template(template_file)
        self.__dbproperties = os.path.join(parentpath,
                                           'data',
                                           'mapping', 
                                           'dbproperties',
                                           'mipmap-db.properties'
                                           )

        self.__create_db_container()
        self.__render_dbproperties()

    def __render_dbproperties(self):
        env = {}
        env['dbusername'] = self.__dbuser
        env['dbpassword'] = self.__dbpassword
        env['dbmipmap'] = self.__mipmapname
        self.__template.stream(env).dump(self.__dbproperties)

    def __create_db_container(self):
        """Creates a postgres 9.6 container.
        """
        self.__check_db_container(mode='running')
        self.__check_db_container(mode='exist')

        if self.__is_db_running:
            LOGGER.info('db container ({}) is already up and'
                        ' running. Skipping creation step...'.format(self.__dbname))
            pass
        elif self.__is_db_exist and not self.__is_db_running:
            LOGGER.info('db container({}) already exists. '
                        'Restarting db container'.format(self.__dbname))
            subprocess.run(['docker', 'restart', self.__dbname])
        else:
            # create the db container
            LOGGER.debug('Creating db container with name {}'.format(self.__dbname))
            arg_port = ['-p', '{}:5432'.format(self.__dbport)]
            arg_name = ['--name', self.__dbname]
            arg_env = ['-e', 'POSTGRES_PASSWORD="{}"'.format(self.__dbpassword)]
            arg_img = ['-d', self.__db_image]
            command2 = ['docker', 'run'] + arg_port + arg_name + arg_env + arg_img
            try:
                createproc = subprocess.run(command2)
            except subprocess.CalledProcessError:
                LOGGER.warning('There was an error while attempting creating the db container.')
                raise DockerExecError('There was an error while attempting creating the db container.')

    def __check_db_container(self, mode='running'):
        """Checks if the db container already running or exist.
        Arguments:
        :param mode: 'running' for container is up and running
                      or 'exist' when container exists but is down.
        """
        if mode == 'running':
            cmd_docker = ['docker', 'ps']
        elif mode == 'exist':
            cmd_docker = ['docker', 'ps', '-a']
        else:
            raise DockerExecError('Invalid container check mode: {}.'.format(mode))


        proc_docker = subprocess.Popen(cmd_docker,
                                       stdout=subprocess.PIPE)
        proc_grep = subprocess.Popen(['grep', self.__dbname],
                                       stdin=proc_docker.stdout,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        stdout, stderr = proc_grep.communicate()
        output = str(stdout).split()
        LOGGER.debug(output)
        try:
            container_image = output[1]
            container_name = output[-1]
            container_port = output[-2]
            # remove new line spacial character
            container_name = container_name.rstrip("\\n'")
            container_port = find_xtport(container_port) 
        except IndexError:
            container_name = None
            container_image = None
            container_port = None
            
        LOGGER.debug('Found that there is an existing container with the name: {}'.format(container_name))

        if container_name == self.__dbname:
            if container_image == self.__db_image:
                if mode == 'running':
                    self.__is_db_running = True
                elif mode == 'exist':
                    self.__is_db_exist = True
                if container_port != self.__dbport:
                    LOGGER.warning('Using as external container port: {}'.format(container_port))
                    self.__dbport = container_port
            else:
                msg = ('The name \"{}\" is used by another container.'
                       'Could not create postgres database container.' 
                       'Please use other db container name.').format(self.__dbname)
                raise DockerExecError(msg)


def find_xtport(strinput):
    external_ip = strinput.split('->')[0]
    external_port = external_ip.split(':')[-1]
    return external_port
