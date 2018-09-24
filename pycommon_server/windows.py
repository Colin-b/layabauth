import logging
import os
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure

logger = logging.getLogger(__name__)


def connect(machine_name: str, ip: str, port: int, domain: str, user_name: str, password: str,) -> SMBConnection:
    logger.info(f'Connecting to {machine_name} ({ip}:{port})...')

    connection = SMBConnection(user_name, password, 'testclient', machine_name, domain=domain, use_ntlm_v2=True, is_direct_tcp=True)
    try:
        if not connection.connect(ip, port):
            raise Exception(f'Impossible to connect to {machine_name} ({ip}:{port}), check connectivity or {domain}\\{user_name} rights.')
    except TimeoutError:
        logger.exception(f'Impossible to connect to {machine_name} ({ip}:{port}), check connectivity or {domain}\\{user_name} rights.')
        raise Exception(f'Impossible to connect to {machine_name} ({ip}:{port}), check connectivity or {domain}\\{user_name} rights.')

    logger.info(f'Connected to {machine_name} ({ip}:{port}).')
    return connection


def get(connection: SMBConnection, share_folder: str, file_path: str, output_file_path: str):
    logger.info(f'Retrieving file \\\\{connection.remote_name}\\{share_folder}{file_path}...')

    with open(output_file_path, 'wb') as file:
        try:
            connection.retrieveFile(share_folder, file_path, file)
        except OperationFailure:
            logger.exception(f'Unable to retrieve \\\\{connection.remote_name}\\{share_folder}{file_path} file')
            raise Exception(f'Unable to retrieve \\\\{connection.remote_name}\\{share_folder}{file_path} file')

    logger.info(f'File \\\\{connection.remote_name}\\{share_folder}{file_path} stored within {output_file_path}.')


def move(connection: SMBConnection, share_folder: str, file_path: str, input_file_path: str, temp_file_suffix='.tmp'):
    logger.info(f'Moving {input_file_path} file to \\\\{connection.remote_name}\\{share_folder}{file_path}...')

    try:
        with open(input_file_path, "rb") as input_file:
            connection.storeFile(share_folder, f'{file_path}{temp_file_suffix}', input_file)
    except OperationFailure:
        logger.exception(f'Unable to write \\\\{connection.remote_name}\\{share_folder}{file_path}{temp_file_suffix} file')
        raise Exception(f'Unable to write \\\\{connection.remote_name}\\{share_folder}{file_path}{temp_file_suffix} file')

    if temp_file_suffix:
        try:
            connection.rename(share_folder, f'{file_path}{temp_file_suffix}', file_path)
        except OperationFailure:
            logger.exception(f'Unable to rename temp file into \\\\{connection.remote_name}\\{share_folder}{file_path}')
            raise Exception(f'Unable to rename temp file into \\\\{connection.remote_name}\\{share_folder}{file_path}')

    logger.info(f'File copied. Removing {input_file_path} file...')
    os.remove(input_file_path)

    logger.info(f'{input_file_path} file moved within \\\\{connection.remote_name}\\{share_folder}{file_path}.')


def rename(connection: SMBConnection, share_folder: str, old_file_path: str, new_file_path: str):
    logger.info(f'Renaming {old_file_path} into {new_file_path}...')
    files_list = None
    try:
        try:
            files_list = connection.listPath(share_folder, os.path.dirname(old_file_path),
                                             pattern=os.path.basename(old_file_path))
        except OperationFailure:
            logger.exception(f"{old_file_path} doesn't exist")

        if files_list:
            connection.rename(share_folder, old_file_path, new_file_path)

    except OperationFailure:
        logger.exception(f'Unable to rename {old_file_path} into {new_file_path}')
        raise Exception(f'Unable to rename {old_file_path} into {new_file_path}')

    logger.info(f'File renamed...')
