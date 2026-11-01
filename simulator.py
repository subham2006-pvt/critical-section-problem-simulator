"""Deterministic, step-by-step educational model of critical-section algorithms."""
from collections import deque
from time import monotonic

ALGORITHMS = {
    "mutex": {
        "name": "Mutex Lock",
        "description": "A lock allows one process at a time into the critical section.",
        "supports": "2–6 processes",
        "complexity": "Low conceptual overhead"
    },
    "semaphore": {
        "name": "Semaphore",
        "description": "A binary semaphore uses wait/signal to control access to a shared resource.",
        "supports": "2–6 processes",
        "complexity": "Low conceptual overhead"
    },
    "peterson": {
        "name": "Peterson's Algorithm",
        "description": "Software mutual exclusion for exactly two processes using flag[] and turn.",
        "supports": "Exactly 2 processes",
        "complexity": "Busy-waiting in theory"
    },
}

class Simulator:
    def __init__(self):
        self.configure("mutex", 3)

    def configure(self, algorithm="mutex", count=3):
        if algorithm not in ALGORITHMS:
            algorithm = "mutex"
        count = 2 if algorithm == "peterson" else max(2, min(int(count), 6))
        self.algorithm = algorithm
        self.count = count
        self.tick = 0
        self.shared_value = 0
        self.owner = None
        self.locked = False
        self.semaphore_value = 1
        self.turn = 0
        self.flags = [False] * count
        self.processes = []
        for i in range(count):
            self.processes.append({
                "id": f"P{i+1}", "state": "Ready", "phase": "remainder",
                "entries": 0, "wait_ticks": 0, "total_ticks": 0,
                "remaining": 0, "last_action": "Created"
            })
        self.events = []
        self.violations = 0
        self.completed_entries = 0
        self._queue = deque(range(count))
        self._log("Simulator initialized", "info")

    def reset(self):
        self.configure(self.algorithm, self.count)
        return self.snapshot()

    def _log(self, message, kind="info"):
        self.events.insert(0, {"time": self.tick, "message": message, "kind": kind})
        self.events = self.events[:60]

    def _next_ready(self):
        for _ in range(len(self._queue)):
            idx = self._queue[0]
            self._queue.rotate(-1)
            if self.processes[idx]["state"] not in ("In Critical Section",):
                return idx
        return None

    def step(self):
        self.tick += 1
        for p in self.processes:
            p["total_ticks"] += 1
            if p["state"] == "Waiting":
                p["wait_ticks"] += 1

        # Each tick models one process transition, not real OS scheduling.
        # Finish the current owner first, so a critical-section entry is released
        # on the following simulated tick rather than being skipped by round-robin.
        active_idx = next((i for i, proc in enumerate(self.processes)
                           if proc["state"] == "In Critical Section"), None)
        idx = active_idx if active_idx is not None else self._next_ready()
        if idx is None:
            self._log("No eligible process this tick", "warning")
            return self.snapshot()
        p = self.processes[idx]
        pid = p["id"]

        if p["state"] == "In Critical Section":
            # Release after one simulated tick in the critical section.
            p["state"] = "Remainder"
            p["phase"] = "remainder"
            p["last_action"] = "Exited critical section"
            self.shared_value += 1
            self.completed_entries += 1
            self.owner = None
            self.locked = False
            self.semaphore_value = 1
            if self.algorithm == "peterson":
                self.flags[idx] = False
            self._log(f"{pid} exits critical section; shared value → {self.shared_value}", "success")
            return self.snapshot()

        # Try to enter.
        can_enter = False
        if self.algorithm == "mutex":
            if not self.locked:
                self.locked = True
                self.owner = pid
                can_enter = True
            else:
                p["state"] = "Waiting"
                p["phase"] = "entry"
                p["last_action"] = "Mutex busy; waiting"
                self._log(f"{pid} waits because mutex is locked", "warning")
        elif self.algorithm == "semaphore":
            if self.semaphore_value > 0:
                self.semaphore_value -= 1
                self.owner = pid
                self.locked = True
                can_enter = True
            else:
                p["state"] = "Waiting"
                p["phase"] = "entry"
                p["last_action"] = "Semaphore unavailable; waiting"
                self._log(f"{pid} waits because semaphore value is 0", "warning")
        else:
            # Peterson's algorithm model: set intent and yield turn to the other process.
            other = 1 - idx
            self.flags[idx] = True
            self.turn = other
            if not self.flags[other] or self.turn == idx:
                can_enter = True
                self.owner = pid
                self.locked = True
            else:
                p["state"] = "Waiting"
                p["phase"] = "entry"
                p["last_action"] = "Peterson condition not satisfied"
                self._log(f"{pid} waits on Peterson's condition", "warning")

        if can_enter:
            # Recover a waiting process into the active state.
            p["state"] = "In Critical Section"
            p["phase"] = "critical"
            p["entries"] += 1
            p["last_action"] = "Entered critical section"
            p["remaining"] = 1
            self._log(f"{pid} acquires access and enters critical section", "success")
        elif p["state"] == "Waiting":
            # Round-robin fairness: a later successful process can release the resource.
            pass
        else:
            p["state"] = "Ready"
            p["phase"] = "entry"
        return self.snapshot()

    def snapshot(self):
        total_wait = sum(p["wait_ticks"] for p in self.processes)
        total_ticks = sum(p["total_ticks"] for p in self.processes)
        entries = sum(p["entries"] for p in self.processes)
        waiting = [p["id"] for p in self.processes if p["state"] == "Waiting"]
        active = [p["id"] for p in self.processes if p["state"] == "In Critical Section"]
        return {
            "algorithm": self.algorithm,
            "algorithm_info": ALGORITHMS[self.algorithm],
            "tick": self.tick,
            "shared_value": self.shared_value,
            "owner": self.owner,
            "locked": self.locked,
            "semaphore_value": self.semaphore_value,
            "turn": self.turn,
            "flags": self.flags,
            "process_count": self.count,
            "processes": self.processes,
            "events": self.events,
            "waiting_queue": waiting,
            "active": active,
            "stats": {
                "entries": entries,
                "completed": self.completed_entries,
                "avg_wait": round(total_wait / self.count, 2) if self.count else 0,
                "throughput": round(self.completed_entries / self.tick, 3) if self.tick else 0,
                "violation_count": self.violations,
                "total_wait": total_wait
            }
        }
