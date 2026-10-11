from core.provider_contracts import ModelResponse, SearchResponse, SearchResult


def test_search_contract_keeps_provider_provenance():
    result = SearchResult(
        title="Example",
        url="https://example.org/paper",
        domain="example.org",
        snippet="Abstract",
        published_at="2026-01-01",
    )
    response = SearchResponse(
        provider="test-provider",
        retrieved_at="2026-01-02T00:00:00+00:00",
        results=(result,),
    )
    assert response.provider == "test-provider"
    assert response.results[0].url.startswith("https://")


def test_model_response_is_plain_metadata():
    response = ModelResponse(provider="local", model="example:small", text="ok", duration_ms=3)
    assert response.local_only if hasattr(response, "local_only") else response.provider == "local"
