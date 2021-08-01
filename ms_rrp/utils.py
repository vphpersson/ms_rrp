from pathlib import PureWindowsPath
from typing import Optional
from uuid import uuid4

from rpc.connection import Connection as RPCConnection
from smb.v2.session import Session as SMBv2Session
from smb.v2.structures.create_options import CreateOptions
from smb.v2.structures.access_mask import FilePipePrinterAccessMask

from ms_rrp.operations.base_reg_save_key import base_reg_save_key, BaseRegSaveKeyRequest
from ms_rrp.operations.base_reg_open_key import base_reg_open_key, BaseRegOpenKeyRequest
from ms_rrp.structures.regsam import Regsam


async def dump_reg(
    rpc_connection: RPCConnection,
    smb_session: SMBv2Session,
    root_key_handle: bytes,
    tree_id: int,
    sub_key_name: str,
    save_path: Optional[PureWindowsPath] = None,
    sam_desired: Regsam = Regsam(maximum_allowed=True),
    delete_file_on_close: bool = True
) -> bytes:
    """
    Dump a specified key, subkeys, and values on a remote system and retrieve the results.

    The dump is performed using the `MS-RRP` `BaseRegSaveKey` operation, which writes the dump to a file on disk. The
    dump file is retrieved from the remote system using the SMB `READ` operation. The file can be opened with the
    `FILE_DELETE_ON_CLOSE` flag, to delete the file when it has been read and closed.

    :param rpc_connection: An RPC connection with which to perform the dump operation via `MS-RRP`s `BaseRegSaveKey`.
    :param smb_session: An SMB session with which to retrieve the dump file.
    :param root_key_handle: A handle to a root registry key.
    :param tree_id: An ID of an opened share via which to retrieve the file on the remote system.
    :param sub_key_name: The name of a registry subkey which to dump.
    :param save_path: The path where the dump file is to be written on the remote system.
    :param sam_desired: The desired access when opening the specified registry key.
    :param delete_file_on_close: Whether to delete the dump file when it has been read and closed.
    :return: The data of the dumped registry key, subkeys, and values.
    """

    save_path = save_path or PureWindowsPath(f'C:\\Windows\\Temp\\{uuid4()}')

    base_reg_open_key_options = dict(
        rpc_connection=rpc_connection,
        request=BaseRegOpenKeyRequest(key_handle=root_key_handle, sub_key_name=sub_key_name, sam_desired=sam_desired)
    )
    async with base_reg_open_key(**base_reg_open_key_options) as base_reg_open_key_response:
        await base_reg_save_key(
            rpc_connection=rpc_connection,
            request=BaseRegSaveKeyRequest(key_handle=base_reg_open_key_response.key_handle, save_path=save_path)
        )

    create_kwargs = dict(
        path=PureWindowsPath(*save_path.parts[1:]),
        tree_id=tree_id,
        create_options=CreateOptions(non_directory_file=True, delete_on_close=delete_file_on_close),
        desired_access=FilePipePrinterAccessMask(file_read_data=True, delete=delete_file_on_close)
    )
    async with smb_session.create(**create_kwargs) as create_response:
        return await smb_session.read(
            file_id=create_response.file_id,
            file_size=create_response.endof_file,
            tree_id=tree_id
        )
