"""
tests/unit/test_ai_validators.py — Tests for AI response validation.
Tests: valid responses, malformed JSON, dangerous content, schema violations.
"""
import pytest

from ai.validators import (
    MitigationResponse,
    ThreatAnalysisResponse,
    _contains_dangerous_content,
    validate_ai_response,
)


class TestValidateAiResponse:
    def test_valid_threat_response(self):
        raw = '{"risk_level": "HIGH", "confidence": 0.85, "impact_summary": "Test impact", "affected_areas": ["logistics"], "recommended_actions": ["act1"], "time_sensitivity": "DAYS"}'
        result = validate_ai_response(raw, ThreatAnalysisResponse)
        assert result is not None
        assert result.risk_level == "HIGH"

    def test_invalid_json(self):
        result = validate_ai_response("not json", ThreatAnalysisResponse)
        assert result is None

    def test_wrong_schema(self):
        raw = '{"risk_level": "INVALID", "confidence": 2.0}'
        result = validate_ai_response(raw, ThreatAnalysisResponse)
        assert result is None

    def test_markdown_wrapped_json(self):
        raw = '```json\n{"risk_level": "LOW", "confidence": 0.5, "impact_summary": "ok", "affected_areas": [], "recommended_actions": [], "time_sensitivity": "WEEKS"}\n```'
        result = validate_ai_response(raw, ThreatAnalysisResponse)
        assert result is not None

    def test_rejects_dangerous_content(self):
        raw = '{"risk_level": "HIGH", "confidence": 0.9, "impact_summary": "os.system(rm -rf /)", "affected_areas": [], "recommended_actions": [], "time_sensitivity": "IMMEDIATE"}'
        result = validate_ai_response(raw, ThreatAnalysisResponse)
        assert result is None


class TestDangerousContent:
    def test_detects_code_execution(self):
        assert _contains_dangerous_content({"cmd": "os.system('ls')"})

    def test_detects_cypher_injection(self):
        assert _contains_dangerous_content({"query": "MATCH (n) DELETE n"})

    def test_safe_content(self):
        assert not _contains_dangerous_content({"msg": "Activate safety stock"})

    def test_nested_detection(self):
        assert _contains_dangerous_content({"a": {"b": [{"c": "exec('code')"}]}})
