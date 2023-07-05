from morbin import Morbin, Output
from dataclasses import dataclass
from pathier import Pathier
from icecream import ic


@dataclass
class Server:
    name: str
    country: str
    protocol: str
    load: str
    plan: str
    features: str


@dataclass(init=False)
class Connection:
    IP: str
    server: Server
    kill_switch: str
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
        self.kill_switch = connection["Kill switch"]
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


if __name__ == "__main__":
    p = Proton()
    print(p.connection)
