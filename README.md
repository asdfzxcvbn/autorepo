# autorepo
automatically update a repo from a telegram channel, powered by starfiles

it goes without saying windows is not supported. use wsl.

# usage
1. install [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#unixmacos), [configure your shell](https://github.com/pyenv/pyenv?tab=readme-ov-file#set-up-your-shell-environment-for-pyenv), [install build dependencies](https://github.com/pyenv/pyenv?tab=readme-ov-file#install-python-build-dependencies), and tmux
2. `pyenv install 3.12`
3. `pyenv global 3.12`
4. install docker/(podman + podman-compose)
5. `pip install -U orjson uvloop "aiohttp[speedups]" aiofiles`
6. `pip install https://github.com/KurimuzonAkuma/pyrogram/archive/v2.1.21.zip --force-reinstall`
7. populate `env.sample.py` and move it to `env.py`
8. `docker-compose up -d` or `podman-compose up -d`, adjusting `docker-compose.yml` as necessary
9. uh point your reverse proxy to the port from `docker-compose.yml`
10. `tmux new-session -t autorepo`
11. `python autorepo.py`
12. press ctrl-b, then d

don't know how to do any of this stuff? too bad! i'm expecting only people who actually know what they're doing to host stuff like this.

ps: if you're using a vps, i heavily recommend using rootless podman over docker, as it wont fuck up your firewall configuration. just adjust your minimum port number to 80 in sysctl, and [enable linger](https://github.com/containers/podman/blob/main/troubleshooting.md#17-rootless-containers-exit-once-the-user-session-exits) (hopefully this saves you hours of time, i know i personally wasted a lot of time on it)
