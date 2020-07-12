from test_init import execute_cmd

import pytest


@pytest.fixture
def get_args():
    args = {
        "Launcher": None,
        "Amsi": "reflection",
        "Transport": "http",
        "ClipExec": "none",
        "Proxy": "false",
        "TLS1.2": "false",
        "Fingerprint": "true",
        "NoVerification": "false",
        "CertStore": "false",
    }
    yield args


def copy_and_execute(filename, payload, interpreter=""):
    import tempfile
    import subprocess
    if isinstance(payload, str):
        tmpf = tempfile.NamedTemporaryFile('w', delete=False)
    else:
        tmpf = tempfile.NamedTemporaryFile('wb', delete=False)
    tmpf.write(payload)
    tmpf.close()

    try:
        execute_cmd(f"ssh win10 del C:/Windows/Temp/{filename}")
    except subprocess.CalledProcessError:
        # this happens if the file does not exist
        pass

    execute_cmd(f"scp {tmpf.name} win10:C:/Windows/Temp/{filename}")
    out = execute_cmd(f"ssh win10 {interpreter} C:/Windows/Temp/{filename}")
    return out


def test_vbs(get_args):
    from powerhub.payloads import create_vbs
    args = get_args
    args['Launcher'] = 'vbs'
    filename, payload = create_vbs(args)
    assert filename == 'powerhub-vbs-reflection-http.vbs'

    out = copy_and_execute(filename, payload, "cscript.exe")
    assert "Windows Script Host" in out
    assert "error" not in out


def test_gcc(get_args):
    from powerhub.payloads import create_exe
    args = get_args
    args['Launcher'] = 'mingw32-64bit'
    filename, payload = create_exe(args)
    assert filename == 'powerhub-mingw32-64bit-reflection-http.exe'
    assert b"DOS" in payload
    assert payload.startswith(b'MZ')

    out = copy_and_execute(filename, payload)
    assert out == ""


def test_mcs(get_args):
    from powerhub.payloads import create_dotnet
    args = get_args
    args['Launcher'] = 'dotnetexe-64bit'
    filename, payload = create_dotnet(args)
    assert filename == 'powerhub-dotnetexe-64bit-reflection-http.exe'
    assert b"DOS" in payload
    assert payload.startswith(b'MZ')

    out = copy_and_execute(filename, payload)

    assert out == ""
