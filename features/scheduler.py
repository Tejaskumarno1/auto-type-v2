"""
Auto Typer Pro — Scheduler
Supports delayed start and scheduled start at a specific time.
Fixed: properly runs callback on the main thread.
"""
import time
import logging
from datetime import datetime, timedelta
from threading import Thread, Event

logger = logging.getLogger("AutoTyper.Scheduler")


class Scheduler:
    """Schedule typing to start after a delay or at a specific time."""

    def __init__(self):
        self.cancel_event = Event()
        self.on_countdown = None  # fn(remaining_secs)  — called from timer thread
        self.on_ready = None     # fn() — called when it's time to start
        self.active = False
        self._thread = None

    def schedule_delay(self, seconds: int):
        """Start typing after N seconds."""
        if self.active:
            self.cancel()
        self.cancel_event.clear()
        self.active = True
        self._thread = Thread(target=self._countdown, args=(seconds,), daemon=True)
        self._thread.start()
        logger.info(f"Scheduled: start in {seconds}s")

    def schedule_time(self, target_hour: int, target_minute: int):
        """Start typing at a specific HH:MM today (or tomorrow if past)."""
        now = datetime.now()
        target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        delta = int((target - now).total_seconds())
        logger.info(f"Scheduled: start at {target_hour:02d}:{target_minute:02d} ({delta}s from now)")
        self.schedule_delay(delta)

    def cancel(self):
        """Cancel the scheduled start."""
        self.cancel_event.set()
        self.active = False
        logger.info("Schedule cancelled")

    def _countdown(self, seconds: int):
        """Internal countdown loop — runs on background thread."""
        for remaining in range(seconds, 0, -1):
            if self.cancel_event.is_set():
                self.active = False
                return
            if self.on_countdown:
                try:
                    self.on_countdown(remaining)
                except Exception as e:
                    logger.error(f"Countdown callback error: {e}")
            time.sleep(1)

        self.active = False
        if not self.cancel_event.is_set() and self.on_ready:
            try:
                self.on_ready()
            except Exception as e:
                logger.error(f"Ready callback error: {e}")
