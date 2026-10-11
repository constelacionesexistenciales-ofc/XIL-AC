from core.research_assessment import assess_source_metadata


def test_assessment_reports_domain_diversity_without_reliability_score():
    results = [
        {"title": "One", "url": "https://one.example/a", "domain": "one.example"},
        {"title": "Two", "url": "https://two.example/b", "domain": "two.example"},
        {"title": "Three", "url": "https://three.example/c", "domain": "three.example"},
    ]

    assessment = assess_source_metadata(results)

    assert assessment["source_count"] == 3
    assert assessment["unique_domain_count"] == 3
    assert assessment["domain_diversity"] == "limited"
    assert assessment["https_source_count"] == 3
    assert assessment["reliability_score"] is None
    assert assessment["content_verified"] is False


def test_assessment_counts_missing_metadata_and_duplicate_urls():
    results = [
        {"title": "", "url": "https://same.example/a", "domain": "same.example"},
        {"url": "https://same.example/a", "domain": ""},
        {"title": "Bad scheme", "url": "http://other.example/b", "domain": "other.example"},
    ]

    assessment = assess_source_metadata(results)

    assert assessment["missing_title_count"] == 2
    assert assessment["missing_domain_count"] == 1
    assert assessment["duplicate_url_count"] == 1
    assert assessment["https_source_count"] == 2


def test_assessment_handles_empty_or_malformed_result_collection():
    assert assess_source_metadata([])["domain_diversity"] == "unavailable"
    assessment = assess_source_metadata([None, "invalid"])
    assert assessment["source_count"] == 2
    assert assessment["unique_domain_count"] == 0
    assert assessment["content_verified"] is False


def test_assessment_normalizes_domain_duplicates():
    results = [
        {"title": "One", "url": "https://example.org/1", "domain": "Example.org"},
        {"title": "Two", "url": "https://example.org/2", "domain": "example.org."},
    ]

    assessment = assess_source_metadata(results)

    assert assessment["unique_domain_count"] == 1
    assert assessment["domain_diversity"] == "insufficient"
