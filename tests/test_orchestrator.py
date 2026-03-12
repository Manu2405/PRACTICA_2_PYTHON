from core import orchestrator


def test_orchestrator_runs():
    results = orchestrator.start_orchestrator()
    assert isinstance(results, list)
    assert len(results) >= 14
    assert all('bank' in r and 'decrypted' in r for r in results)


def test_orchestrator_contains_union():
    from core.orchestrator import BANKS
    assert any(b['name'] == 'Banco Unión S.A.' for b in BANKS)
    assert any(b['id'] == 'bank_union' for b in BANKS)

