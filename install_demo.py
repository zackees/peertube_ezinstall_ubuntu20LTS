import os
import sys
import subprocess
import platform


def exec_shell(cmd: str) -> int:
    print(f"Running {cmd}:")
    rtn = os.system(cmd)
    if rtn != 0:
        print(f"Warning, executing \n  {cmd}\n  returned code {rtn}")
    return rtn


def exec_stdout(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True)

def system_name() -> str:
    if sys.platform == 'win32':
        return platform.uname().system
    else:
        return platform.uname().node

def system_version() -> str:
    return platform.uname().version


def main() -> None:
    if 'ubuntu' != system_name():
        print(f"Error, this script is only tested for ubuntu, you are running {system_name()}.")
        sys.exit(1)
    elif '20.04' not in system_version():
        print(f"Warning, this script is only tested on Ubuntu 20.04LTS, you are running {system_version()}")

    exec_shell("sudo apt update")
    exec_shell("sudo apt install python3-dev python-is-python3")
    exec_shell("sudo apt update")
    exec_shell(
        "sudo apt install certbot nginx ffmpeg postgresql postgresql-contrib openssl g++ make redis-server git cron wget"
    )
    # exec_shell('ffmpeg -version') should be >= 4.1
    # exec_shell('g++ -v') # Should be >= 5.x
    exec_shell("sudo systemctl start redis postgresql")
    exec_shell("sudo useradd -m -d /var/www/peertube -s /bin/bash -p peertube peertube")
    exec_shell("echo peertube | sudo passwd peertube")
    os.chdir("/var/www/peertube")
    exec_shell(
        "sudo -u postgres createdb -O peertube -E UTF8 -T template0 peertube_prod")
    exec_shell('sudo -u postgres psql -c "CREATE EXTENSION pg_trgm;" peertube_prod')
    exec_shell('sudo -u postgres psql -c "CREATE EXTENSION unaccent;" peertube_prod')
    version_str = exec_stdout(
        '''curl -s https://api.github.com/repos/chocobozzz/peertube/releases/latest | grep tag_name | cut -d '"' -f 4''',
    ).strip()
    os.chdir("/var/www/peertube")
    exec_shell("sudo -u peertube mkdir config storage versions")
    exec_shell("sudo -u peertube chmod 750 config/")
    os.chdir("/var/www/peertube/versions")
    exec_shell(
        f'sudo -u peertube wget -q "https://github.com/Chocobozzz/PeerTube/releases/download/${version_str}/peertube-${version_str}.zip"'
    )
    exec_shell(
        f"sudo -u peertube unzip -q peertube-${version_str}.zip && sudo -u peertube rm peertube-${version_str}.zip"
    )
    os.chdir("/var/www/peertube")
    exec_shell(
        f"sudo -u peertube ln -s versions/peertube-${version_str} ./peertube-latest")
    os.chdir("./peertube-latest")
    exec_shell("sudo -H -u peertube yarn install --production --pure-lockfile")
    os.chdir("/var/www/peertube")
    exec_shell(
        "sudo -u peertube cp peertube-latest/config/default.yaml config/default.yaml"
    )
    os.chdir("/var/www/peertube")
    exec_shell(
        "sudo -u peertube cp peertube-latest/config/production.yaml.example config/production.yaml"
    )
    print(
        "\n\nFinished installation, please edit config/production.yaml\nThen visit https://docs.joinpeertube.org/install-any-os?id=truck-webserver to continue installation."
    )

if __name__ == "__main__":
    main()
    sys.exit(0)
