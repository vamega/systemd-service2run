### systemd-service2run

A simple python script that can take a systemd service and outputs a
`systemd-run` invocation that should give you an interactive shell that reflects
environment the service would run in.

### Motivation

I was working on setting up some systemd services on nixos and in trying to
implement the principles of least separation I kept running into permissions
issues. I wanted to debug those services, and an interactive shell that
reflected the permissions of the service seemed perfect.

I learnt of `systemd-run` in this [blog post][dynamic-users-blog-post] from
Lennart Poettering. He has a lot of systemd-run invocations in that post, but on
nixos the paths to executables, and packages is far too long, and I didn't want
to copy paste these in a terminal.

I couldn't find anything within systemd to take a service's unit file, and run a
shell for it, so I wrote this. It's almost certainly incomplete, and there are
probably a lot of features of the unit file spec that are missing from this
script. Feel free to contribute to this script if something you know want is
missing.

If this can be done within systemd-itself, please let me know.

[dynamic-users-blog-post]: https://0pointer.net/blog/dynamic-users-with-systemd.html
