#!/usr/bin/env python3
"""Record a REAL command run into an asciinema v3 cast with true timing.

Runs the command under a pseudo-terminal and timestamps each output chunk with
a monotonic clock, so timing is accurate even in a headless/non-TTY environment
(plain `asciinema rec` collapses timing without a real TTY). Writes relative
inter-event deltas, as asciinema v3 expects.

    python demo/record_live.py demo/demo.cast -- bash demo.sh
"""
import json
import os
import pty
import select
import struct
import sys
import time

COLS, ROWS = 100, 30
IDLE_CAP = 2.0  # cap long gaps (e.g. model load) so playback stays snappy


def record(cmd, cast_path):
    events = []
    pid, fd = pty.fork()
    if pid == 0:  # child
        os.environ["COLUMNS"], os.environ["LINES"] = str(COLS), str(ROWS)
        os.environ["TERM"] = "xterm-256color"
        os.execvp(cmd[0], cmd)
        os._exit(1)

    # parent: set the pty window size, then read until EOF
    try:
        import termios
        import fcntl
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
    except Exception:
        pass

    last = time.monotonic()
    while True:
        try:
            r, _, _ = select.select([fd], [], [], 1.0)
        except (OSError, ValueError):
            break
        if fd in r:
            try:
                data = os.read(fd, 65536)
            except OSError:
                break
            if not data:
                break
            now = time.monotonic()
            dt = min(now - last, IDLE_CAP)
            last = now
            events.append([round(dt, 3), "o", data.decode("utf-8", "replace")])
    try:
        os.close(fd)
    except OSError:
        pass
    os.waitpid(pid, 0)

    header = {"version": 3, "term": {"cols": COLS, "rows": ROWS},
              "idle_time_limit": IDLE_CAP, "title": "Resume RAG + Job Matcher"}
    with open(cast_path, "w") as f:
        f.write(json.dumps(header) + "\n")
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    dur = sum(e[0] for e in events)
    print(f"wrote {cast_path} ({len(events)} events, {dur:.1f}s)")


if __name__ == "__main__":
    if "--" not in sys.argv:
        print("usage: record_live.py <out.cast> -- <command...>", file=sys.stderr)
        sys.exit(2)
    sep = sys.argv.index("--")
    out = sys.argv[1]
    command = sys.argv[sep + 1:]
    record(command, out)
