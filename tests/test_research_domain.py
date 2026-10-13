from core.research import _query_for_domain


def test_general_domain_does_not_modify_query():
    assert _query_for_domain("decision making", "general") == "decision making"


def test_science_domain_adds_search_context():
    query = _query_for_domain("decision making", "science")
    assert query.startswith("decision making ")
    assert "scientific research studies evidence" in query


def test_cfe_domain_adds_cfe_context():
    query = _query_for_domain("belonging", "cfe")
    assert "Constelaciones Familiares y Existenciales CFE" in query


def test_unknown_domain_fails_closed():
    from core.research import ResearchProviderNotConfigured
    import pytest

    with pytest.raises(ResearchProviderNotConfigured):
        _query_for_domain("anything", "unapproved-domain")
