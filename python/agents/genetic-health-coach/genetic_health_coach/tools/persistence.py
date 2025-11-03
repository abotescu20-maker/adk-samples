"""Utilities for persisting generated reports."""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

try:  # pragma: no cover - optional dependency only used when available
    from ftplib import FTP
except ImportError:  # pragma: no cover - documented behavior
    FTP = None  # type: ignore


def persist_report(
    *,
    content: str,
    destination: str,
    encoding: str = "utf-8",
    ftp_username: Optional[str] = None,
    ftp_password: Optional[str] = None,
    ftp_directory: Optional[str] = None,
) -> str:
    """Persist the generated report to a local path or FTP server.

    Parameters
    ----------
    content:
        The textual report that should be saved.
    destination:
        Either an absolute/relative local file path or an FTP URL of the form
        ``ftp://host[:port]/path/to/file.txt``.
    encoding:
        Encoding used when writing text files locally or through FTP.
    ftp_username / ftp_password:
        Optional credentials for FTP uploads. If omitted the function attempts
        to perform an anonymous login.
    ftp_directory:
        Optional directory to ``cwd`` into after login when using FTP. The
        directory will not be created automatically, keeping the helper safe by
        default. Users can pre-create the directory manually if needed.

    Returns
    -------
    str
        A human readable confirmation message describing where the content was
        written.

    Raises
    ------
    ValueError
        If the destination is invalid or FTP support is unavailable.
    RuntimeError
        If the FTP transfer fails.
    """

    parsed = urlparse(destination)

    if parsed.scheme in {"", "file"}:
        # Local file system persistence.
        path = Path(parsed.path if parsed.scheme else destination).expanduser()
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
        return f"Raport salvat local la: {path}"

    if parsed.scheme != "ftp":
        raise ValueError(
            "Destinația trebuie să fie o cale locală sau un URL FTP (ftp://...)."
        )

    if FTP is None:  # pragma: no cover - environment dependent
        raise ValueError("Modulul ftplib nu este disponibil în mediul curent.")

    host = parsed.hostname
    if not host:
        raise ValueError("URL-ul FTP trebuie să includă un hostname valid.")

    port = parsed.port or 21
    remote_path = parsed.path.lstrip("/")
    if not remote_path:
        raise ValueError("URL-ul FTP trebuie să includă o cale de fișier.")

    try:  # pragma: no cover - network interactions not exercised in tests
        with FTP() as ftp:
            ftp.connect(host, port)
            ftp.login(user=ftp_username or "anonymous", passwd=ftp_password or "")

            if ftp_directory:
                ftp.cwd(ftp_directory)

            # Ensure subdirectories from the remote_path exist.
            directories, filename = os.path.split(remote_path)
            if directories:
                for segment in directories.split("/"):
                    if not segment:
                        continue
                    try:
                        ftp.mkd(segment)
                    except Exception:  # noqa: BLE001
                        # Ignore if directory already exists.
                        pass
                    ftp.cwd(segment)

            ftp.storbinary(
                f"STOR {filename}",
                io.BytesIO(content.encode(encoding)),
            )
    except Exception as exc:  # pragma: no cover - network interactions
        raise RuntimeError("Încărcarea către serverul FTP a eșuat.") from exc

    return f"Raport încărcat pe FTP la: ftp://{host}/{remote_path}"


__all__ = ["persist_report"]
