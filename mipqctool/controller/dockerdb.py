import subprocess

import os
import time
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
        # contain name
        self.__db_cont_name = name
        self.__dbport = port
        self.__dbuser = MIPMAP_DB_USER
        self.__dbpassword = password
        self.__is_db_exist = False
        self.__is_db_running = False
        # the data base name
        self.__mipmapdb = MIPMAP_DB_NAME

        lib_path = os.path.abspath(os.path.dirname(__file__))
        thispath = Path(lib_path)
        parentpath = str(thispath.parent)
        env_path = os.path.join(parentpath, 'data', 'templates')
        env = Environment(loader=FileSystemLoader(env_path))
        template_file = 'mipmap-db.properties.j2'
        self.__template = env.get_template(template_file)


        self.__create_db_container()

    def render_dbproperties(self, folderpath):
        env = {}
        env['dbusername'] = self.__dbuser
        env['dbpassword'] = self.__dbpassword
        env['dbmipmap'] = self.__mipmapdb
        propertiespath = os.path.join(folderpath, 'mipmap-db.properties')
        self.__template.stream(env).dump(propertiespath)

    def __create_db_container(self):
        """Creates a postgres 9.6 container.
        """
        self.__check_db_container(mode='running')
        self.__check_db_container(mode='exist')

        if self.__is_db_running:
            LOGGER.info('db container ({}) is already up and'
                        ' running. Skipping creation step...'.format(self.__db_cont_name))
            self.__remove_create_db()
            pass
        elif self.__is_db_exist and not self.__is_db_running:
            LOGGER.info('db container({}) already exists. '
                        'Restarting db container'.format(self.__db_cont_name))
            subprocess.run(['docker', 'restart', self.__db_cont_name])
            time.sleep(10)
            self.__remove_create_db()

        else:
            # create the db container
            LOGGER.debug('Creating db container with name {}'.format(self.__db_cont_name))
            arg_port = ['-p', '{}:5432'.format(self.__dbport)]
            arg_name = ['--name', self.__db_cont_name]
            arg_env1 = ['-e', 'POSTGRES_PASSWORD={}'.format(self.__dbpassword)]
            arg_env2 = ['-e', 'POSTGRES_USER={}'.format(self.__dbuser)]
            arg_img = ['-d', self.__db_image]
            command2 = ['docker', 'run'] + arg_port + arg_name + arg_env1 + arg_env2 + arg_img
            try:
                createproc = subprocess.run(command2)
                time.sleep(50)
                self.__remove_create_db()
            except subprocess.CalledProcessError:
                LOGGER.warning('There was an error while attempting creating the db container.')
                raise DockerExecError('There was an error while attempting creating the db container.')

    def __remove_create_db(self):
        command1 = ['docker', 'exec', '-it', self.__db_cont_name, 'psql']
        arg_1 = ['-U', self.__dbuser, '-d', 'postgres']
        arg_c_remove = ['-c', '"DROP DATABASE IF EXISTS {};"'.format(self.__mipmapdb)]

        arg_c_create = ['-c', '"CREATE DATABASE {};"'.format(self.__mipmapdb)]
        removeproc = subprocess.run(command1 + arg_1 + arg_c_remove)
        createproc = subprocess.run(command1 + arg_1 + arg_c_create)

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
        proc_grep = subprocess.Popen(['grep', self.__db_cont_name],
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

        if container_name == self.__db_cont_name:
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
                       'Please use other db container name.').format(self.__db_cont_name)
                raise DockerExecError(msg)


def find_xtport(strinput):
    external_ip = strinput.split('->')[0]
    external_port = external_ip.split(':')[-1]
    return external_port
