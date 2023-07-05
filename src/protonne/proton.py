from morbin import Morbin, Output
from dataclasses import dataclass
from pathier import Pathier


@dataclass
class Server:
    name: str
    country: str
    protocol: str
    load: str
    plan: str
    features: str


@dataclass(init=False)
class KillSwitch:
    on: bool
    active: bool
    permanent: bool

    def __init__(self, status: str):
        if status == "Off":
            self.on = False
            self.active = False
            self.permenent = False
        elif status.startswith("On (Inactive,"):
            self.on = True
            self.active = False
            self.permanent = False
        elif status == "On":
            self.on = True
            self.active = True
            self.permanent = False
        elif status == "Permanent":
            self.on = True
            self.active = True
            self.permanent = True


@dataclass(init=False)
class Connection:
    IP: str
    server: Server
    killswitch: KillSwitch
    time: str
    raw: str

    def __init__(self, status: str):
        self.raw = status
        lines = [line for line in status.splitlines() if ":" in line]
        connection = {
            line.split(":", 1)[0]: line.split(":", 1)[1].replace("\t", "").strip()
            for line in lines
        }
        self.IP = connection["IP"]
        self.server = Server(
            connection["Server"],
            connection["Country"],
            connection["Protocol"],
            connection["Server Load"],
            connection["Server Plan"],
            connection["Server Features"],
        )
        self.killswitch = KillSwitch(connection["Kill switch"])
        self.time = connection["Connection time"]

    def __str__(self) -> str:
        return self.raw


class Proton(Morbin):
    def proton(self, args: str = "") -> Output:
        """Base function for executing `protonvpn-cli` commands.

        Higher level commands should be built on this function and return its output."""
        return self.execute("protonvpn-cli", args)

    # Seat |=============================== Core ===============================|

    def status(self) -> Output:
        """Execute status command."""
        return self.proton("status")

    def killswitch(self, arg: str) -> Output:
        """`arg` should be one of `on`, `off`, or `permanent`."""
        return self.proton(f"killswitch --{arg}")

    # Seat |=========================== Convenience ===========================|

    @property
    def connected(self) -> bool:
        """Returns whether this device is connected to Proton."""
        with self.capturing_output():
            status = self.status().stdout
        return "Proton VPN Connection Status" in status

    @property
    def connection(self) -> Connection | None:
        """If this device is connected, a `Connection` object will be returned.
        If disconnected, `None` will be returned.

        Accessing this property can be time consuming due to the protonvpn-cli backend.
        Ideally store it in a local variable until you need to check for an updated connection status.
        """
        with self.capturing_output():
            if self.connected:
                return Connection(self.status().stdout)
            return None

    def enable_killswitch(self) -> Output:
        return self.killswitch("on")

    def disable_killswitch(self) -> Output:
        return self.killswitch("off")

    def enable_permanent_killswitch(self) -> Output:
        return self.killswitch("permanent")


if __name__ == "__main__":
    p = Proton(True)
    text = p.proton("config --help").stdout
    Pathier("scratch.txt").write_text(text)
    """ 
Proton VPN CLI v3.13.0

For bugs and errors, please use the form https://protonvpn.com/support-form
or send a report to support@protonvpn.com.

usage:  protonvpn-cli [--version | --help] <command>

commands:
    login               Login with Proton VPN credentials.
    logout              Disconnect, remove Proton VPN connection and logout.
    c, connect          Connect to Proton VPN.
    d, disconnect       Disconnect from Proton VPN.
    s, status           Show connection status.
    r, reconnect        Reconnect to previously connected server.
    config              Configure user settings.
    ks, killswitch      Configure Kill Switch settings.
    ns, netshield       Configure NetShield settings.

optional arguments:
    -h, --help          Display help message.
    -v, --version       Display versions.
    --get-logs          Get Proton VPN logs.

examples:
    protonvpn-cli login
    protonvpn-cli login --help
    protonvpn-cli logout
    protonvpn-cli (c | connect)
    protonvpn-cli (c | connect) --help
    protonvpn-cli (d | disconnect)
    protonvpn-cli (s | status)
    protonvpn-cli (r | reconnect)
    protonvpn-cli config
    protonvpn-cli config --help
    protonvpn-cli (-h | --help)
    protonvpn-cli (-v | --version)
    protonvpn-cli --get-logs



usage:  protonvpn-cli login [-h | --help] <pvpn_username>

positional arguments:
    <pvpn_username> Proton VPN Username

optional arguments:
    -h, --help      Display help message.

examples:
    protonvpn-cli login pvpn_username
    protonvpn-cli login --help



usage:  protonvpn-cli (c | connect) [-h | --help] 
        [[<servername> | [-f | --fastest] | [-r | --random] | --cc | --sc | --p2p | --tor] [-p | --protocol] <protocol>]]

positional arguments:
    <servername>    Directly connecto to
                    specified server (ie: CH#4, CH-US-1, HK5-Tor).

optional arguments:
    -f, --fastest   Connect to the fastest Proton VPN server.
    -r, --random    Connect to a random Proton VPN server.
    --cc            Connect to the specified country code (SE, PT, BR, AR).
    --sc            Connect to the fastest Secure-Core server.
    --p2p           Connect to the fastest P2P server.
    --tor           Connect to the fastest Tor server.
    -p , --protocol Connect via specified protocol.
    -h, --help      Display help message.

examples:
    protonvpn-cli connect PT#8 -p tcp
    protonvpn-cli connect --fastest --protocol udp
    protonvpn-cli c --cc PT -p tcp
    protonvpn-cli c --sc
    protonvpn-cli c --p2p -p tcp
    protonvpn-cli connect --tor
    protonvpn-cli c --random --protocol udp
    protonvpn-cli c --help



usage:  protonvpn-cli config [-h | --help]
        [[--list | -l] | --dns <command> [--ip <IP>] | [-p | --protocol] <protocol> | [-d | --default] | --vpn-accelerator | --alt-routing]

optional arguments:
    --dns <command>     Change DNS configurations
                        (custom | automatic).
    --ip                Custom DNS IP (max 3 IPs).
    -l, --list          List all configurations.
    -p, --protocol      Change default protocol.
    -d, --default       Reset to default configurations.
    --alt-routing       Change alternative routing preference.
    --moderate-nat      Change Moderate NAT preference.
                        If disabled then strict NAT is applied.
    --non-standard-ports Change Non Standard Ports preference.
                        If disabled then a limited ammount of ports will be used for improved security.
    --vpn-accelerator   VPN Accelerator enables a set of unique performance
                        enhancing technologies which can increase VPN speeds by up to 400%.
    -h, --help          Display help message.

examples:
    protonvpn-cli config --dns automatic
    protonvpn-cli config --dns custom --ip 192.168.0.1
    protonvpn-cli config (-l | --list)
    protonvpn-cli config -p tcp
    protonvpn-cli config --protocol udp
    protonvpn-cli config --vpn-accelerator enable
    protonvpn-cli config --alt-routing enable
    protonvpn-cli config --moderate-nat disable
    protonvpn-cli config (-d | --default)
    protonvpn-cli config --help

usage:  protonvpn-cli (ns | netshield) [-h | --help]
        [--off | --malware | --ads-malware]

optional arguments:
    --off           Disable NetShield.
    --malware       Block malware.
    --ads-malware   Block malware, ads, & trackers
    -h, --help      Display help message.

examples:
    protonvpn-cli (ns | netshield) --malware
    protonvpn-cli (ns | netshield) --ads-malware
    protonvpn-cli (ns | netshield) --off
    protonvpn-cli (ns | netshield) --help

 """
