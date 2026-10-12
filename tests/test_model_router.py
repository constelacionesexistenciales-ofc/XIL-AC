import pytest

from core.model_router import ModelRouteUnavailable, ModelRouter


def test_general_task_uses_configured_general_model():
    route = ModelRouter({"general": "local/qwen3-instruct"}).route("general")
    assert route.model_id == "local/qwen3-instruct"
    assert route.local_only is False


def test_privacy_sensitive_task_requires_local_model():
    route = ModelRouter({"local": "local/qwen3-instruct"}).route("privacy_sensitive")
    assert route.local_only is True
    assert route.model_id.startswith("local/")


def test_privacy_sensitive_task_rejects_remote_model():
    router = ModelRouter({"local": "provider/model-name"})
    with pytest.raises(ModelRouteUnavailable, match="privacy_route_must_be_local"):
        router.route("privacy_sensitive")


def test_missing_route_fails_closed():
    with pytest.raises(ModelRouteUnavailable, match="model_route_not_configured"):
        ModelRouter({}).route("reasoning")


def test_research_and_coding_can_use_distinct_models():
    router = ModelRouter({"research": "local/qwen3", "coding": "local/deepseek-r1"})
    assert router.route("research").model_id == "local/qwen3"
    assert router.route("coding").model_id == "local/deepseek-r1"


def test_unknown_task_fails_closed():
    with pytest.raises(ModelRouteUnavailable, match="unsupported_task"):
        ModelRouter({}).route("unlisted")  # type: ignore[arg-type]
