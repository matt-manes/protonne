from pathlib import Path

from protonne import Proton

proton = Proton()


def test_login():
    proton.login(input("Proton username: "))


def test_connect():
    proton.connect_fastest()
    assert proton.connected
    connection = proton.connection
    assert connection
    print("\n" + str(connection) + "\n")


def test_disconnect():
    proton.disconnect()
    assert not proton.connected
    assert proton.connection is None


def test__clear_cache():
    path = Path.home() / ".cache" / "protonvpn"
    proton.clear_cache()
    assert len(list(path.glob("*.*"))) == 0


def test_killswitch():
    proton.connect_random()
    ks = proton.connection.killswitch  # type: ignore
    assert not ks.on and not ks.active and not ks.permanent
    proton.enable_killswitch()
    ks = proton.connection.killswitch  # type: ignore
    assert ks.on and not ks.active and not ks.permanent
    proton.reconnect()
    ks = proton.connection.killswitch  # type: ignore
    assert ks.on and ks.active and not ks.permanent
    proton.enable_permanent_killswitch()
    ks = proton.connection.killswitch  # type: ignore
    assert ks.on and ks.active and ks.permanent
    proton.disable_killswitch()
    ks = proton.connection.killswitch  # type: ignore
    assert not ks.on and not ks.active and not ks.permanent
