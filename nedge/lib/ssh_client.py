import paramiko
import re

from common import Output

cprint = Output()

class SSHClient():

    def __init__(self, ssh_to, login, passwd, port=22):
        self._ssh_to, self._port = ssh_to, int(port)
        self._login, self._passwd = login, passwd
        self._ansi_escape_rx = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        self._transport = None
        self._session = None
        self._channel = None
        self._channel_fd = None

    def _create_transport(self):
        # TODO: Run in retry loop if network connectivity is found to be unstable
        try:
            self._transport = paramiko.Transport('%s:%s' % (self._ssh_to, self._port))
            self._transport.set_keepalive(10)
            self._transport.connect(username=self._login, password=self._passwd)
        except paramiko.BadAuthenticationType:
            cprint.colorPrint('public-key authentication not allowed on %s for %s' % (self._ssh_to, self._login), 'r')
            raise
        except paramiko.AuthenticationException:
            cprint.colorPrint('Authentication failed for %s on %s' % (self._login, self._ssh_to), 'r')
            raise
        except Exception as e:
            cprint.colorPrint('Error in getting transport object for %s (Error: %s)' % (self._ssh_to, e), 'r')
            raise

    def _create_session(self):
        if self._transport is None:
            self._create_transport()

        if self._session is None:
            self._session = self._transport.open_session()
            self._session.set_combine_stderr(True)

    def _create_channel(self, timeout=10.0):
        """
        Create a secure tunnel across an SSH Transport.
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

        try:
            connection = client.connect(self._ssh_to, username=self._login, \
                password=self._passwd, banner_timeout=2.0)
        except Exception as e:
            cprint.colorPrint('Could not do SSH connect to %s. Error: %s' % (self._ssh_to, e), 'r')
	    #raise Exception("ERROR")

        try:
            self._channel = client.invoke_shell()
            self._channel.settimeout(timeout)
            # To avoid gc of SSHClient object associated with the channel
            self._channel.keep_this = client
        except SSHException as e:
            cprint.colorPrint('Could not open SSH channel on %s. Error: %s' % (self._ssh_to, e), 'r')
	    #raise Exception("ERROR")
        self._channel_fd = self._channel.fileno()

    def run(self, cmd):
        rc, output = None, None

        try:
            self._create_session()
            print '%s: Executing: %s' % (self._ssh_to, cmd)
            self._session.exec_command(cmd)
            output = ''
            while True:
                content = self._session.recv(4096)
                if not content:
                    break
                output += content
            rc = self._session.recv_exit_status()
            # Note: Every command execution is a new session
            # Close current so that a new execution can be done
            self._session.close()
            #output = output.rstrip()
        except Exception as e:
            cprint.colorPrint('Console output: %s' % e, 'r')

        self._session = None
        #colorPrint('Execution results: rc[%s], output:[%s]' % (rc, output), 'g')
        return rc, output

#if __name__ == '__main__':
#	main()
