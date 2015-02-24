import sched, time, asyncore

class asynschedcore(sched.scheduler):
    """Combine sched.scheduler and asyncore.loop."""
    # On receiving a signal asyncore kindly restarts select. However the signal
    # handler might change the scheduler instance. This tunable determines the
    # maximum time in seconds to spend in asycore.loop before reexamining the
    # scheduler.
    maxloop = 30
    def __init__(self, map=None):
        sched.scheduler.__init__(self, time.time, self._delay)
        if map is None:
            self._asynmap = asyncore.socket_map
        else:
            self._asynmap = map
        self._abort_delay = False

    def _maybe_abort_delay(self):
        if not self._abort_delay:
            return False
        # Returning from this function causes the next event to be executed, so
        # it might be executed too early. This can be avoided by modifying the
        # head of the queue. Also note that enterabs sets _abort_delay to True.
        self.enterabs(0, 0, lambda:None, ())
        self._abort_delay = False
        return True

    def _delay(self, timeout):
        if self._maybe_abort_delay():
            return
        if 0 == timeout:
            # Should we support this hack, too?
            # asyncore.loop(0, map=self._asynmap, count=1)
            return
        now = time.time()
        finish = now + timeout
        while now < finish and self._asynmap:
            asyncore.loop(min(finish - now, self.maxloop), map=self._asynmap,
                          count=1)
            if self._maybe_abort_delay():
                return
            now = time.time()
        if now < finish:
            time.sleep(finish - now)

    def enterabs(self, *args, **kwargs):
        # We might insert an event before the currently next event.
        self._abort_delay = True
        return sched.scheduler.enterabs(self, *args, **kwargs)

    # Overwriting enter is not necessary, because it is implemented using enter.

    def cancel(self, event):
        # We might cancel the next event.
        self._abort_delay = True
        return sched.scheduler.cancel(self, event)

    def run(self):
        """Runs as long as either an event is scheduled or there are
        sockets in the map."""
        while True:
            if not self.empty():
                sched.scheduler.run(self)
            elif self._asynmap:
                asyncore.loop(self.maxloop, map=self._asynmap, count=1)
            else:
                break