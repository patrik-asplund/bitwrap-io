"""
bitwrap_io.api

this module defines a json-rpc api using cyclone.io
"""
from cyclone.jsonrpc import JsonrpcRequestHandler
from bitwrap_io.api import headers
import bitwrap_io


class Handler(headers.Mixin, JsonrpcRequestHandler):
    """
    Invoke transform actions on PNML state machines
    """

    def jsonrpc_preview(self, msg):
        """ preview a state machine transformation"""
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

        return bitwrap_io.open(msg['schema']).preview(**msg)

    def jsonrpc_transform(self, msg):
        """ execute a state machine transformation"""
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

        msg['ip'] = self.request.remote_ip
        msg['endpoint'] = self.request.host

        return bitwrap_io.open(msg['schema'])(**msg)
