#!/usr/bin/env python3
"""Capture the safe robot's USB serial log to files, and analyse it.

  live:     python3 logger.py --port /dev/tty.usbmodem14101
            Writes runs/<stamp>_raw.log (every line, with the computer's time)
            and runs/<stamp>_attempts.csv (one row per ATT line). Lines you
            type are sent to the robot (start, resume, pause, status, ! ...),
            so you don't need the Arduino Serial Monitor (only one program can
            have the port open).
  replay:   python3 logger.py --replay runs/<stamp>_raw.log
            Rebuilds the attempts CSV from a raw log.
  analyse:  python3 logger.py --analyse runs/<stamp>_attempts.csv
            Re-classifies every attempt from its raw key angle: clean fail /
            false set / success, using the spread of this run's clean fails.

Opening the port resets the Mega (Arduino auto-reset). That's harmless — the
firmware keeps its progress in EEPROM — but start the logger *before*
`start`, and don't restart it during a run unless you mean to `resume`.

Needs pyserial for live mode only:  python3 -m pip install pyserial
"""
import argparse
import csv
import datetime as dt
import os
import statistics
import sys
import threading

ATT_FIELDS = ["ms", "index", "a", "b", "c", "key_steps", "key_deg", "stalled", "sg_min", "cls", "n_deg"]
CSV_FIELDS = ["host_time"] + ATT_FIELDS + ["delta_deg"]
SHOW = ("EV,", "ERR,", "SUCCESS,", "NSTOP,", "RECHECK,", "HOME,", "LEARN,", "DRV,", "#", "CFG,", "SG,")


def parse_att(line):
    """'ATT,ms,index,a,b,c,keySteps,keyDeg,stalled,sgMin,class,nDeg' -> dict, or None."""
    if not line.startswith("ATT,"):
        return None
    parts = line.strip().split(",")[1:]
    if len(parts) != len(ATT_FIELDS):
        return None
    row = dict(zip(ATT_FIELDS, parts))
    try:
        for k in ("ms", "index", "a", "b", "c", "key_steps", "stalled", "sg_min"):
            row[k] = int(row[k])
        row["key_deg"] = float(row["key_deg"])
        row["n_deg"] = float(row["n_deg"])
    except ValueError:
        return None
    row["delta_deg"] = round(row["key_deg"] - row["n_deg"], 1)
    return row


def split_raw(raw_line):
    """Raw log lines are '<host ISO time>\\t<robot line>'."""
    if "\t" in raw_line:
        t, line = raw_line.rstrip("\n").split("\t", 1)
        return t, line
    return "", raw_line.rstrip("\n")


def replay(raw_path, csv_path):
    n = 0
    with open(raw_path) as f, open(csv_path, "w", newline="") as out:
        w = csv.DictWriter(out, fieldnames=CSV_FIELDS)
        w.writeheader()
        for raw in f:
            t, line = split_raw(raw)
            row = parse_att(line)
            if row:
                row["host_time"] = t
                w.writerow(row)
                n += 1
    return n


def load_attempts(csv_path):
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["delta_deg"] = float(r["delta_deg"])
        r["key_deg"] = float(r["key_deg"])
        r["stalled"] = int(r["stalled"])
        r["index"] = int(r["index"])
    return rows


def analyse(rows, clean_tol=None, success_min=10.0, k=6.0):
    """Classify from delta = angle - N. The clean band comes from the data:
    median + k * MAD of all deltas (most attempts are clean fails), unless
    clean_tol is given. Returns (summary dict, rows with 'offline_cls')."""
    deltas = [r["delta_deg"] for r in rows]
    if not deltas:
        return {"attempts": 0}, rows
    med = statistics.median(deltas)
    mad = statistics.median([abs(d - med) for d in deltas]) or 0.1
    band = clean_tol if clean_tol is not None else med + k * 1.4826 * mad
    counts = {"CLEAN": 0, "FALSESET": 0, "SUCCESS": 0, "EARLY": 0}
    for r in rows:
        d = r["delta_deg"]
        if d >= success_min:
            c = "SUCCESS"
        elif d < med - max(band - med, 1.0) * 3:
            c = "EARLY"
        elif d <= band:
            c = "CLEAN"
        else:
            c = "FALSESET"
        r["offline_cls"] = c
        counts[c] += 1
    disagree = sum(1 for r in rows if r.get("cls") and r["cls"] != r["offline_cls"])
    summary = {"attempts": len(rows), "median_delta": round(med, 2), "mad": round(mad, 2),
               "clean_band": round(band, 2), **counts, "firmware_disagrees": disagree}
    return summary, rows


def print_analysis(summary, rows, top=20):
    print("attempts: {attempts}  median(angle-N): {median_delta} deg  MAD: {mad} deg  clean band: <= {clean_band} deg".format(**summary))
    print("CLEAN {CLEAN}  FALSESET {FALSESET}  SUCCESS {SUCCESS}  EARLY {EARLY}  (firmware classes that differ: {firmware_disagrees})".format(**summary))
    cands = sorted(rows, key=lambda r: -r["delta_deg"])[:top]
    print(f"\nlargest angles past N (top {top}): index, dials a-b-c, delta deg, firmware class, offline class")
    for r in cands:
        print(f"  {r['index']:5d}  {r['a']:>2}-{r['b']:>2}-{r['c']:>2}  {r['delta_deg']:+6.1f}  {r.get('cls',''):9s} {r['offline_cls']}")


def live(port, baud, outdir):
    import serial  # pyserial

    os.makedirs(outdir, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    raw_path = os.path.join(outdir, f"{stamp}_raw.log")
    csv_path = os.path.join(outdir, f"{stamp}_attempts.csv")
    ser = serial.Serial(port, baud, timeout=0.2)
    print(f"logging to {raw_path} and {csv_path}; type commands, Ctrl-C to quit")

    def keyboard():
        for cmd in sys.stdin:
            ser.write(cmd.strip().encode() + (b"" if cmd.strip() == "!" else b"\n"))

    threading.Thread(target=keyboard, daemon=True).start()
    n = 0
    with open(raw_path, "a") as raw, open(csv_path, "w", newline="") as out:
        w = csv.DictWriter(out, fieldnames=CSV_FIELDS)
        w.writeheader()
        buf = b""
        try:
            while True:
                buf += ser.read(256)
                while b"\n" in buf:
                    b, buf = buf.split(b"\n", 1)
                    line = b.decode(errors="replace").rstrip("\r")
                    now = dt.datetime.now().isoformat(timespec="milliseconds")
                    raw.write(f"{now}\t{line}\n")
                    raw.flush()
                    row = parse_att(line)
                    if row:
                        row["host_time"] = now
                        w.writerow(row)
                        out.flush()
                        n += 1
                        if row["cls"] != "CLEAN" or n % 50 == 0:
                            print(f"{now[11:19]} attempt {row['index']} {row['a']}-{row['b']}-{row['c']} "
                                  f"{row['key_deg']} deg ({row['delta_deg']:+}) {row['cls']}  [{n} logged]")
                    elif line.startswith(SHOW):
                        print(f"{now[11:19]} {line}")
                    if line.startswith("SUCCESS,"):
                        print("\a*** SUCCESS — see the line above ***")
        except KeyboardInterrupt:
            pass
    print(f"\n{n} attempts logged")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--port", help="serial port of the Mega")
    g.add_argument("--replay", metavar="RAW_LOG", help="rebuild the attempts CSV from a raw log")
    g.add_argument("--analyse", metavar="ATTEMPTS_CSV", help="re-classify attempts from their angles")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--out", default="runs", help="output folder for live mode")
    ap.add_argument("--clean", type=float, help="clean-fail band in deg past N (default: from the data)")
    ap.add_argument("--success", type=float, default=10.0, help="deg past N that counts as success")
    a = ap.parse_args(argv)
    if a.port:
        live(a.port, a.baud, a.out)
    elif a.replay:
        out = a.replay.replace("_raw.log", "") + "_attempts.csv"
        print(f"{replay(a.replay, out)} attempts -> {out}")
    else:
        summary, rows = analyse(load_attempts(a.analyse), a.clean, a.success)
        print_analysis(summary, rows)


if __name__ == "__main__":
    main()
