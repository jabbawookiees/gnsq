# -*- coding: utf-8 -*-
from __future__ import absolute_import
import blinker
from .errors import NSQException


class Message(object):
    """A class representing a message received from nsqd.

    **Signals:**

    .. data:: on_finish(reader, message)
        :noindex:

        Sent when successfully finished.

    .. data:: on_requeue(reader, message, timeout)
        :noindex:

        Sent when requeued.

    .. data:: on_touch(reader, message)
        :noindex:

        Sent when touched.
    """

    def __init__(self, timestamp, attempts, id, body):
        self.timestamp = timestamp
        self.attempts = attempts
        self.id = id
        self.body = body

        self._has_responded = False
        self.on_finish = blinker.Signal()
        self.on_requeue = blinker.Signal()
        self.on_touch = blinker.Signal()

    def has_responded(self):
        """Returns whether or not this message has been responded to."""
        return self._has_responded

    def finish(self):
        """
        Respond to nsqd that you’ve processed this message successfully
        (or would like to silently discard it).
        """
        if self._has_responded:
            raise NSQException('already responded')
        self._has_responded = True
        self.on_finish.send(self)

    def requeue(self, time_ms=0):
        """
        Respond to nsqd that you’ve failed to process this message successfully
        (and would like it to be requeued).
        """
        if self._has_responded:
            raise NSQException('already responded')
        self._has_responded = True
        self.on_requeue.send(self, timeout=time_ms)

    def touch(self):
        """Respond to nsqd that you need more time to process the message."""
        if self._has_responded:
            raise NSQException('already responded')
        self.on_touch.send(self)
