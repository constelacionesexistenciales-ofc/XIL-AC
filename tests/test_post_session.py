from core.post_session import (
    REQUIRED_ORDER,
    PostSessionBlocked,
    PostSessionRequest,
    Stage,
    run_post_session,
)


def make_request(**overrides):
    values = dict(
        execution_id="exec-test-001",
        session_id="session-synthetic-001",
        transcript="FACILITADOR: ¿Qué notás?\nCONSULTANTE: Me siento más tranquilo.",
        session_end_confirmed=True,
        synthetic_data=True,
        processing_enabled=False,
    )
    values.update(overrides)
    return PostSessionRequest(**values)


def make_handlers(calls=None):
    calls = calls if calls is not None else []

    def handler_for(stage):
        def handler(request, previous):
            calls.append(stage)
            return f"salida-{stage.value}"

        return handler

    return {stage: handler_for(stage) for stage in REQUIRED_ORDER}


def test_runs_all_stages_in_required_order_and_requires_review():
    calls = []
    result = run_post_session(make_request(), make_handlers(calls))
    assert tuple(calls) == REQUIRED_ORDER
    assert tuple(item.stage for item in result.stages) == REQUIRED_ORDER
    assert result.status == "awaiting_human_review"
    assert result.human_review_required is True
    assert len(result.transcript_sha256) == 64


def test_blocks_when_session_end_is_not_confirmed():
    try:
        run_post_session(make_request(session_end_confirmed=False), make_handlers())
    except PostSessionBlocked as exc:
        assert "no fue confirmado" in str(exc)
    else:
        raise AssertionError("Expected close confirmation gate to block")


def test_blocks_real_sessions_while_feature_flag_is_off():
    try:
        run_post_session(
            make_request(synthetic_data=False, processing_enabled=False), make_handlers()
        )
    except PostSessionBlocked as exc:
        assert "deshabilitado" in str(exc)
    else:
        raise AssertionError("Expected real-session gate to block")


def test_blocks_missing_handler_before_running_any_stage():
    calls = []
    handlers = make_handlers(calls)
    handlers.pop(Stage.CONSULTANT_REPORT)
    try:
        run_post_session(make_request(), handlers)
    except PostSessionBlocked as exc:
        assert "Falta" in str(exc)
    else:
        raise AssertionError("Expected incomplete pipeline to block")
    assert calls == []


def test_blocks_if_a_stage_fails_without_exposing_handler_error():
    handlers = make_handlers()
    handlers[Stage.PROCESS_AUDIT] = lambda *_: (_ for _ in ()).throw(
        RuntimeError("sensitive transcript fragment")
    )
    try:
        run_post_session(make_request(), handlers)
    except PostSessionBlocked as exc:
        assert "sensitive transcript fragment" not in str(exc)
        assert Stage.PROCESS_AUDIT.value in str(exc)
    else:
        raise AssertionError("Expected handler failure to block")
