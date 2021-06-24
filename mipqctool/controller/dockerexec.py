import subprocess

from mipqctool.config import LOGGER
from mipqctool.controller.dockerdb import DockerDB
from mipqctool.controller.dockermipmap import DockerMipmap
from mipqctool.exceptions import DockerExecError

class DockerExec(object):
    def __init__(self, name, port, password, mapping, source, target, output):
        """Class for checking if the docker client is installed. Also 
        checks if the user belongs to docker usergroup.
        Arguments:
        :param name: db container name
        :param port: the external port of the db container
        :param password: password for the postgres user
        :param mapping: folderpath containing the mapping xml file
        :param source: folderpath with the source csv file
        :param target: folderpath with the target csv file
        :param output: folderpath where the output file will be saved
        """

        if not self.__check_docker_client():
            raise DockerExecError('Docker client could not be found.')
        elif not self.__check_usergroup():
            raise DockerExecError('User is not belong to docker usergroup')
        else:
            self.dbcontainer = DockerDB(name=name, port=port, password=password)
            self.mipmapcontainer = DockerMipmap(mapping=mapping,
                                                source=source,
                                                target=target,
                                                output=output)

    def __check_usergroup(self):
        LOGGER.debug('Checking if user is in docker usergroup')
        process = subprocess.Popen(['groups'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = process.communicate()
        groups = output.decode('utf-8').split()
        if 'docker' in groups:
            return True
        else:
            return False

    def __check_docker_client(self):
        
        LOGGER.debug('Checking if docker client exist.')
        process = subprocess.Popen(['which', 'docker'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = process.communicate()
        decoded = output.decode('utf-8')
        if decoded != '':
            return True
        else:
            return False

