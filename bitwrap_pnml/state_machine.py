"""
bitwrap_pnml.state_machine

Combine storage and machine modules to provide a persitent state machine object
"""
import os
from txrdq.rdq import ResizableDispatchQueue
from twisted.internet import defer

from bitwrap_pnml.storage import Storage
from bitwrap_pnml.machine import Machine

class StateMachine(object):
    """
    State Machine object with persistant storage
    """

    def __init__(self, schema):
        self.schema = schema.__str__()
        self.machine = Machine(self.schema)

    def session(self, request):
        """ start a session """
        return Transaction(self.machine, self.schema, request)

    def transform(self, msg):
        """ execute a tranformation """
        return self.session(msg).commit()

    def preview(self, msg):
        """ simulate a tranformation """
        return self.session(msg).simulate()

    @staticmethod
    def __handler__(txn):
        if not txn.response.called:
            txn.response.callback(txn.persist())

TXN_QUEUE = ResizableDispatchQueue(StateMachine.__handler__, 1)

class Transaction(object):
    """ state machine transaction """

    def __init__(self, machine, schema, request):
        self.schema = schema
        self.request = request
        self.response = defer.Deferred()
        self.machine = machine
        self.dry_run = False

    def simulate(self):
        """ simulate transform and return cache values """
        self.dry_run = True
        return self.execute()

    def commit(self):
        """ transform and persist state to storage """
        return self.execute()

    def execute(self):
        """ run transformation """
        TXN_QUEUE.put(self)
        return self.response

    def persist(self):
        """ persist to storage """
        stor = Storage.open(self.schema)
        return stor.commit(self.machine, self.request, dry_run=self.dry_run)