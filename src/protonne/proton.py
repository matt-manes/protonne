from morbin import Morbin, Output


class Proton(Morbin):
    def proton(self, args: str = "") -> Output:
        """Base function for executing `protonvpn-cli` commands.

        Higher level commands should be built on this function and return its output."""
        return self.execute("protonvpn-cli", args)
