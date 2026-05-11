import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from environment.grid import Grid
from environment.hazards import AstrophageManager
from agents.grace import Grace
from agents.rocky import Rocky


def make_both():
    grid = Grid()
    mgr = AstrophageManager(grid)
    grace = Grace(1, 1, grid, mgr)
    rocky = Rocky(18, 1, grid, mgr)
    rocky.grace_ref = grace
    return grace, rocky, grid, mgr


def test_rocky_starts_alive():
    _, rocky, _, _ = make_both()
    assert rocky.is_alive()
    print("PASS: Rocky starts alive")


def test_rocky_move_costs_energy():
    _, rocky, _, _ = make_both()
    before = rocky.energy
    rocky.move(1, 0)
    assert rocky.energy < before
    print("PASS: Rocky move costs energy")


def test_tunnel_not_connected_at_start():
    _, rocky, _, _ = make_both()
    assert rocky.tunnel_connected is False
    print("PASS: Tunnel not connected at start")


def test_tunnel_builds_progressively():
    _, rocky, _, _ = make_both()
    for _ in range(10):
        rocky.build_tunnel()
    assert rocky.tunnel_build_progress == 10
    assert rocky.tunnel_connected is False
    print("PASS: Tunnel builds progressively (10/15)")


def test_tunnel_completes_after_15():
    _, rocky, _, _ = make_both()
    for _ in range(15):
        rocky.build_tunnel()
    assert rocky.tunnel_connected is True
    print("PASS: Tunnel complete after 15 turns")


def test_cannot_share_without_tunnel():
    grace, rocky, _, _ = make_both()
    result = rocky.share_knowledge()
    assert result is False
    print("PASS: Rocky cannot share knowledge without tunnel")


def test_share_works_with_tunnel():
    grace, rocky, _, _ = make_both()
    for _ in range(15):
        rocky.build_tunnel()
    rocky.energy = 100
    before = grace.knowledge.knowledge_score()
    rocky.share_knowledge()
    after = grace.knowledge.knowledge_score()
    assert after != before
    print(f"PASS: Rocky shares via tunnel ({before:.1f} -> {after:.1f}%)")


def test_transfer_energy_to_grace():
    grace, rocky, _, _ = make_both()
    grace.energy = 30
    rocky.energy = 100
    rocky.transfer_energy()
    assert grace.energy > 30
    assert rocky.energy < 100
    print("PASS: Rocky transferred Astrophage fuel energy to Grace")


def test_no_transfer_when_rocky_low():
    grace, rocky, _, _ = make_both()
    rocky.energy = 20
    result = rocky.transfer_energy()
    assert result is False
    print("PASS: Rocky refuses transfer when own energy low")


def test_erid_progress_updates():
    _, rocky, _, _ = make_both()
    before = rocky.erid_progress
    rocky._update_erid_knowledge("recon")
    rocky._update_erid_knowledge("recon")
    after = rocky.erid_progress
    assert after > before
    print(f"PASS: Erid progress updates ({before:.2f} -> {after:.2f}%)")


def test_erid_independent_from_grace():
    grace, rocky, _, _ = make_both()
    rocky._update_erid_knowledge("recon")
    rocky._update_erid_knowledge("sample_nearby")
    grace_k = grace.knowledge.knowledge_score()
    erid_k  = rocky.erid_progress
    assert erid_k != grace_k
    print(f"PASS: Erid progress ({erid_k:.1f}%) independent from Grace ({grace_k:.1f}%)")


def test_translation_builds_with_tunnel():
    grace, rocky, _, _ = make_both()
    for _ in range(15):
        rocky.build_tunnel()
    rocky.energy = 150
    for _ in range(10):
        rocky.share_knowledge()
        rocky.energy = 150
    assert rocky.translation.vocab_size() > 0
    assert rocky.translation.decoded_size() >= 0
    print(f"PASS: Translation vocab={rocky.translation.vocab_size()} decoded={rocky.translation.decoded_size()} fluency={rocky.translation.fluency:.2f}")


def test_chord_consistent():
    _, rocky, _, _ = make_both()
    chord1 = rocky.translation.rocky_emit("test_signal")
    chord2 = rocky.translation.rocky_emit("test_signal")
    assert chord1 == chord2
    print(f"PASS: Rocky chord consistent ('{chord1}')")


def test_both_survive_50_turns():
    grace, rocky, _, mgr = make_both()
    for _ in range(50):
        grace.decide_action()
        rocky.decide_action()
        mgr.step()
    assert grace.is_alive()
    assert rocky.is_alive()
    print(f"PASS: Both survive 50 turns | G_HP:{grace.health} R_HP:{rocky.health} Tunnel:{rocky.tunnel_connected}")


if __name__ == "__main__":
    test_rocky_starts_alive()
    test_rocky_move_costs_energy()
    test_tunnel_not_connected_at_start()
    test_tunnel_builds_progressively()
    test_tunnel_completes_after_15()
    test_cannot_share_without_tunnel()
    test_share_works_with_tunnel()
    test_transfer_energy_to_grace()
    test_no_transfer_when_rocky_low()
    test_erid_progress_updates()
    test_erid_independent_from_grace()
    test_translation_builds_with_tunnel()
    test_chord_consistent()
    test_both_survive_50_turns()
    print("\nAll Part C tests passed.")
