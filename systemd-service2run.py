#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3

import os
import shlex
import sys
from pwd import getpwnam
from typing import Callable

DEFAULT_SHELL = "/bin/sh"

# Global variable to represent the args for systemd-run
# The shell if specificed manually (as opposed to with --shell) seems like it's
# required to come after the options. Using a global here since it's a one off
# and I don't think anything more complex is needed for now.
_systemd_run_command = ""


def transform_user(value: str) -> list[str]:
    """
    systemd-run seems to only allow specifying the user by uid, so transform
    the name to a uid. Also use the current shell if the user if the users
    shell is set to nologin, since otherwise the unit will immediately exit.
    """
    user_entry = getpwnam(value)
    result = ["--uid", str(user_entry.pw_uid)]

    if user_entry.pw_shell.endswith("nologin"):
        global _systemd_run_command
        _systemd_run_command = os.environ.get("SHELL", DEFAULT_SHELL)
        result += ["--pty", "--wait", "--collect"]
    else:
        result += ["--shell"]
    return result


def transform_group(value: str) -> list[str]:
    """
    systemd-run seems to only allow specifying the group by gid, so transform
    the name to a gid.
    """
    user_entry = getpwnam(value)
    return ["--gid", str(user_entry.pw_gid)]


def transform_dynamic_user(value) -> list[str]:
    """
    systemd-run seems to give dynamic users a nologin shell.
    So isntead of using --shell, use the expanded version, and provide the
    shell as the command.
    """
    global _systemd_run_command
    _systemd_run_command = os.environ.get("SHELL", DEFAULT_SHELL)
    return ["-p", "DynamicUser=true" "--pty", "--wait", "--collect"]


def main():
    if len(sys.argv) == 2:
        stream = open(sys.argv[1], "r")
    else:
        stream = sys.stdin

    excluded_prefixes = ["Exec", "Restart"]
    service_section = False
    real_line_value = ""

    property_translations: dict[str, Callable[str, list[str]]] = {
        "User": transform_user,
        "Group": transform_group,
        "DynamicUser": transform_dynamic_user,
        # Not using WorkingDirectory, since it seems like it works just fine if
        # supplied as a property.
    }

    command = ["systemd-run"]

    for line in stream:
        line = line.rstrip()
        if line.startswith("[Service]"):
            service_section = True
            continue

        if service_section and line.startswith("["):
            service_section = False
            break

        if not line.strip():
            continue

        if line.endswith("\\"):
            real_line_value += line[:-1]
            continue

        real_line_value += line

        if service_section and not any(
            real_line_value.startswith(p) for p in excluded_prefixes
        ):
            prop, _, value = real_line_value.partition("=")
            if prop in property_translations:
                command += property_translations[prop](value)
            else:
                command += ["-p", real_line_value]

        real_line_value = ""

    command += [_systemd_run_command]
    print(shlex.join(command))


if __name__ == "__main__":
    main()
