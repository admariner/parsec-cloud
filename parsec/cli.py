from os import environ
from socket import socket, AF_UNIX, SOCK_STREAM
import click

from parsec.server import UnixSocketServer, WebSocketServer
from parsec.backend import (InMemoryMessageService, MockedVlobService,
                            MockedNamedVlobService, MockedBlockService)
from parsec.core import (BackendAPIService, CryptoService, FileService, GNUPGPubKeysService,
                         IdentityService, ShareService, UserManifestService)
from parsec.ui.shell import start_shell


CORE_UNIX_SOCKET = '/tmp/parsec'


@click.group()
def cli():
    pass


@click.command()
@click.argument('id')
@click.argument('args', nargs=-1)
def cmd(id, args):
    sock = socket(AF_UNIX, SOCK_STREAM)
    sock.connect(CORE_UNIX_SOCKET)
    try:
        msg = '%s %s' % (id, args)
        sock.send(msg.encode())
        resp = sock.recv(4096)
        print(resp)
    finally:
        sock.close()


@click.command()
@click.option('--socket', '-s', default=CORE_UNIX_SOCKET,
              help='Path to the UNIX socket (default: %s).' % CORE_UNIX_SOCKET)
def shell(socket):
    start_shell(socket)


@click.command()
@click.argument('mountpoint', type=click.Path(exists=True, file_okay=False))
@click.option('--identity', type=click.STRING, default=None)
@click.option('--debug', '-d', is_flag=True, default=False)
@click.option('--nothreads', is_flag=True, default=False)
@click.option('--socket', '-s', default=CORE_UNIX_SOCKET,
              help='Path to the UNIX socket (default: %s).' % CORE_UNIX_SOCKET)
def fuse(mountpoint, identity, debug, nothreads, socket):
    # Do the import here in case fuse is not an available dependency
    from parsec.ui.fuse import start_fuse
    start_fuse(socket, mountpoint, identity, debug=debug, nothreads=nothreads)


@click.command()
@click.option('--socket', '-s', default=CORE_UNIX_SOCKET,
              help='Path to the UNIX socket exposing the core API (default: %s).' %
              CORE_UNIX_SOCKET)
@click.option('--backend-host', '-H', default='ws://localhost:6777')
def core(socket, backend_host):
    server = UnixSocketServer()
    server.register_service(BackendAPIService(backend_host))
    server.register_service(CryptoService())
    server.register_service(FileService())
    server.register_service(GNUPGPubKeysService())
    server.register_service(IdentityService())
    server.register_service(ShareService())
    server.register_service(UserManifestService())
    print('Starting parsec core on %s (connecting to backend %s)' % (socket, backend_host))
    server.start(socket)
    print('Bye ;-)')


@click.command()
@click.option('--gnupg-homedir', default='~/.gnupg')
@click.option('--host', '-H', default=None, help='Host to listen on (default: localhost)')
@click.option('--port', '-P', default=None, type=int, help=('Port to listen on (default: 6777)'))
@click.option('--no-client-auth', is_flag=True,
    help='Disable authentication handshake on client connection (default: false)')
def backend(host, port, gnupg_homedir, no_client_auth):
    host = host or environ.get('HOST', 'localhost')
    port = port or int(environ.get('PORT', 6777))
    pub_keys_service = GNUPGPubKeysService(gnupg_homedir)
    if no_client_auth:
        server = WebSocketServer()
    else:
        server = WebSocketServer(pub_keys_service.handshake)
    server.register_service(pub_keys_service)
    server.register_service(InMemoryMessageService())
    server.register_service(MockedVlobService())
    server.register_service(MockedNamedVlobService())
    server.register_service(MockedBlockService())
    print('Starting parsec backend on %s:%s' % (host, port))
    server.start(host, port)
    print('Bye ;-)')


cli.add_command(cmd)
cli.add_command(fuse)
cli.add_command(shell)
cli.add_command(core)
cli.add_command(backend)


if __name__ == '__main__':
    cli()
