from hdfs import InsecureClient
from pathlib import Path
from typing import List, Optional, Union, Generator
import json
from io import BytesIO, IOBase
import os
from utils.logger import logger
from utils.config import config


class HadoopClient:
    """
    HadoopClient provides a reusable interface to interact with Hadoop Distributed File System (HDFS)
    via WebHDFS using the `hdfs` Python library. It supports dynamic input/output handling and is designed
    to work in any Python-based data engineering pipeline or analytics project.

    Args:
        hdfs_url (str): Base URL of the WebHDFS endpoint (e.g., "http://localhost:9870").
        user (str): The Hadoop user identity used for HDFS access (default is set from config).
    """

    def __init__(self, hdfs_url: str = config.HADOOP_URL, user: str = config.HADOOP_USER):
        self.client = InsecureClient(hdfs_url, user=user)
        logger.info(f"✅ Connected to HDFS at {hdfs_url} as user '{user}'")

    def mkdir(self, path: str):
        """
        Create one or more directories in HDFS.

        Args:
            path (str): HDFS directory path to create.
        """
        self.client.makedirs(path)
        logger.info(f"📁 Created directory: {path}")

    def list(self, path: str) -> List[str]:
        """
        List contents of a directory in HDFS.

        Args:
            path (str): HDFS path to list.

        Returns:
            List[str]: List of files and directories at the given path.
        """
        contents = self.client.list(path)
        logger.info(f"📂 Listing contents of {path}: {contents}")
        return contents

    def upload(self, hdfs_path: str, local_path: Union[str, Path], overwrite: bool = True):
        """
        Upload a local file or directory to HDFS.

        Args:
            hdfs_path (str): Destination path in HDFS.
            local_path (str or Path): Path to the local file or directory.
            overwrite (bool): Overwrite existing files if True.
        """
        self.client.upload(hdfs_path, str(local_path), overwrite=overwrite)
        logger.info(f"⬆️ Uploaded '{local_path}' to HDFS path '{hdfs_path}'")

    def download(self, hdfs_path: str, local_path: Union[str, Path], overwrite: bool = True):
        """
        Download a file or directory from HDFS to the local filesystem.

        Args:
            hdfs_path (str): Path to file or directory in HDFS.
            local_path (str or Path): Destination path on local filesystem.
            overwrite (bool): Overwrite local file if it exists.
        """
        self.client.download(hdfs_path, str(local_path), overwrite=overwrite)
        logger.info(f"⬇️ Downloaded '{hdfs_path}' to local path '{local_path}'")

    def read(self, hdfs_path: str) -> Union[str, bytes]:
        """
        Read the contents of a file from HDFS. Automatically detects if binary or text.

        Args:
            hdfs_path (str): HDFS file path.

        Returns:
            str or bytes: File contents as a string or raw bytes.
        """
        try:
            with self.client.read(hdfs_path, encoding="utf-8") as reader:
                return reader.read()
        except UnicodeDecodeError:
            with self.client.read(hdfs_path) as reader:
                return reader.read()

    def write(self, hdfs_path: str, data, overwrite: bool = True, binary: Optional[bool] = None):
        """
        Write content to HDFS. Accepts dict, str, bytes, Path, or file-like objects.

        Args:
            hdfs_path (str): Target path in HDFS.
            data: The content to write. Can be dict, str, bytes, file-like object, or local file path.
            overwrite (bool): Overwrite if file already exists.
            binary (bool): Force binary write. If None, determined automatically.
        """
        try:
            logger.debug(f"🧪 Attempting to write to HDFS: {hdfs_path}")
            logger.debug(f"🧬 Detected data type: {type(data).__name__}")

            if isinstance(data, dict):
                logger.debug("🧾 Serializing dictionary to JSON")
                data = json.dumps(data, indent=2)
                binary = False

            if isinstance(data, Path) and data.exists():
                logger.info(f"📁 Uploading from Path object")
                self.client.upload(hdfs_path, str(data), overwrite=overwrite)
                logger.info(f"⬆️ Written file from Path to HDFS: {hdfs_path}")
                return

            if isinstance(data, str):
                try:
                    # Check if it's a file path
                    local_path = Path(data)
                    if local_path.exists():
                        logger.info(f"📁 Uploading from string path: {local_path}")
                        self.client.upload(hdfs_path, str(local_path), overwrite=overwrite)
                        logger.info(f"⬆️ Written file from string path to HDFS: {hdfs_path}")
                        return
                except Exception as e:
                    logger.warning(f"⚠️ Not a valid path string, treating as raw string: {e}")

                if binary is False or binary is None:
                    logger.info("📝 Writing raw string content to HDFS")
                    with self.client.write(hdfs_path, encoding="utf-8", overwrite=overwrite) as writer:
                        writer.write(data)
                    logger.info(f"📝 Written text content to HDFS: {hdfs_path}")
                    return

            if isinstance(data, (bytes, BytesIO)) or binary:
                logger.info("🧬 Writing binary data to HDFS")
                with self.client.write(hdfs_path, overwrite=overwrite) as writer:
                    if isinstance(data, BytesIO):
                        writer.write(data.getvalue())
                    else:
                        writer.write(data)
                logger.info(f"🧬 Written binary content to HDFS: {hdfs_path}")
                return

            if isinstance(data, IOBase):
                logger.info("📦 Writing stream data to HDFS")
                with self.client.write(hdfs_path, overwrite=overwrite) as writer:
                    for chunk in data:
                        writer.write(chunk)
                logger.info(f"📦 Written stream to HDFS: {hdfs_path}")
                return

            raise TypeError(f"Unsupported data type for HDFS write: {type(data)}")

        except Exception as e:
            logger.exception(f"❌ Failed to write to HDFS path {hdfs_path}: {e}")
            raise

    def delete(self, path: str, recursive: bool = True):
        """
        Delete a file or directory from HDFS.

        Args:
            path (str): HDFS path to delete.
            recursive (bool): If True, delete subdirectories/files recursively.
        """
        self.client.delete(path, recursive=recursive)
        logger.info(f"❌ Deleted path '{path}' from HDFS")

    def exists(self, path: str) -> bool:
        """
        Check if a path exists in HDFS.

        Args:
            path (str): HDFS path to check.

        Returns:
            bool: True if path exists, False otherwise.
        """
        exists = self.client.status(path, strict=False) is not None
        logger.info(f"🔍 Path '{path}' exists: {exists}")
        return exists

    def rename(self, src_path: str, dest_path: str):
        """
        Move or rename a file or directory in HDFS.

        Args:
            src_path (str): Source HDFS path.
            dest_path (str): Destination HDFS path.
        """
        self.client.rename(src_path, dest_path)
        logger.info(f"🔄 Renamed or moved '{src_path}' to '{dest_path}'")

    def status(self, path: str) -> Optional[dict]:
        """
        Fetch file or directory metadata from HDFS.

        Args:
            path (str): HDFS path to inspect.

        Returns:
            dict or None: File metadata if path exists, else None.
        """
        status = self.client.status(path, strict=False)
        logger.info(f"📊 Status for '{path}': {status}")
        return status

    def walk(self, hdfs_path: str) -> Generator:
        """
        Recursively iterate over directories in HDFS similar to os.walk().

        Args:
            hdfs_path (str): HDFS root path to walk.

        Yields:
            Tuple[str, List[str], List[str]]: Directory path, subdirectories, and files.
        """
        for dirpath, dirnames, filenames in self.client.walk(hdfs_path):
            logger.info(f"🚶 Walk at '{dirpath}': {filenames}")
            yield dirpath, dirnames, filenames
