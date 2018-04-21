import os
import sys
from pathlib import Path

from pew.pew import _detect_shell
from pew._utils import temp_environ, invoke_pew as invoke
from pew._win_utils import SHELL_NAMES as WIN_SHELL_NAMES
from utils import skip_windows
import pytest


WIN_SHELL_NAMES = ['python'] + WIN_SHELL_NAMES
win_shell_exes = ['{0}.exe'.format(shell) for shell in WIN_SHELL_NAMES]
check_env = [sys.executable, '-c', "import os; print(os.environ['VIRTUAL_ENV'])"]
check_cwd = [sys.executable, '-c', "import pathlib; print(pathlib.Path().absolute())"]

def test_detect_shell():
    with temp_environ():
        try:
            del os.environ['SHELL']
        except KeyError:
            pass
        if sys.platform == 'win32':
            assert _detect_shell() in win_shell_exes + WIN_SHELL_NAMES
        else:
            assert _detect_shell() == 'sh'
        os.environ['SHELL'] = 'foo'
        assert _detect_shell() == 'foo'


@skip_windows(reason='cannot supply stdin to powershell')
def test_workon(env1):
    cmd = '{0} {1} "{2}"'.format(*check_env)
    out = invoke('workon', 'env1', inp=cmd).out
    assert 'env1' == os.path.basename(out.splitlines()[-1].strip())


def test_workon_no_arg(env1, env2):
    result = invoke('workon')
    out = result.out
    envs = [ x.strip() for x in out.split() ]

    assert 0 == result.returncode
    assert 'env1' in envs
    assert 'env2' in envs


@skip_windows(reason='cannot supply stdin to powershell')
def test_in(env1):
    cmd = '{0} {1} "{2}"'.format(*check_env)
    out = invoke('in', 'env1', inp=cmd).out
    assert 'env1' == os.path.basename(out.splitlines()[-1].strip())


def test_no_symlink(env1):
    getexe = ['python', '-c', "import sys; print(sys.executable)"]
    env = invoke('in', 'env1', *check_env).out
    exe = invoke('in', 'env1', *getexe).out
    assert exe.lower().startswith(env.lower())


def test_no_pew_workon_home(workon_home):
    with temp_environ():
        os.environ['WORKON_HOME'] += '/not_there'
        assert 'does not exist' in invoke('workon', 'doesnt_exist').err


def test_invalid_pew_workon_env_name(workon_home):
    with temp_environ():
        assert 'Invalid environment' in invoke('workon', '/home/toto').err


@skip_windows(reason='cannot supply stdin to powershell')
def test_workon_project(env_with_project):
    project_dir = env_with_project
    cmd = '{0} {1} "{2}"'.format(*check_cwd)
    out = invoke('workon', 'env_with_project', inp=cmd).out
    assert project_dir == Path(out.splitlines()[-1].strip())


@skip_windows(reason='cannot supply stdin to powershell')
def test_workon_project_but_here(env_with_project):
    cwd = Path().absolute()
    cmd = '{0} {1} "{2}"'.format(*check_cwd)
    out = invoke('workon', 'env_with_project', '--here', inp=cmd).out
    assert cwd == Path(out.splitlines()[-1].strip())
