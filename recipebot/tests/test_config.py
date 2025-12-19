"""Tests for configuration parsing functionality."""

import pytest

from recipebot.config.config import AppSettings


@pytest.mark.parametrize(
    "input_value,expected_output,description",
    [
        pytest.param(
            "123456789, 987654321",
            [123456789, 987654321],
            "Normal comma-separated IDs",
            id="normal_comma_separated",
        ),
        pytest.param(
            "123, 456, 789",
            [123, 456, 789],
            "Multiple IDs with spaces",
            id="multiple_with_spaces",
        ),
        pytest.param(
            "42",
            [42],
            "Single ID",
            id="single_id",
        ),
        pytest.param(
            "",
            [],
            "Empty string",
            id="empty_string",
        ),
        pytest.param(
            '"123456789, 987654321"',
            [123456789, 987654321],
            "Double quotes around entire string",
            id="double_quotes",
        ),
        pytest.param(
            "'123456789, 987654321'",
            [123456789, 987654321],
            "Single quotes around entire string",
            id="single_quotes",
        ),
        pytest.param(
            "  123456789, 987654321  ",
            [123456789, 987654321],
            "Extra spaces around values",
            id="extra_spaces_values",
        ),
        pytest.param(
            "  123456789  ,   987654321   ",
            [123456789, 987654321],
            "Extra spaces around commas",
            id="extra_spaces_commas",
        ),
        pytest.param(
            "\t123456789,\n987654321\t",
            [123456789, 987654321],
            "Tabs and newlines",
            id="tabs_newlines",
        ),
        pytest.param(
            "123456789,",
            [123456789],
            "Trailing comma",
            id="trailing_comma",
        ),
        pytest.param(
            ",123456789",
            [123456789],
            "Leading comma",
            id="leading_comma",
        ),
        pytest.param(
            "123456789,,987654321",
            [123456789, 987654321],
            "Double comma",
            id="double_comma",
        ),
        pytest.param(
            "  ,  123456789  ,  ,  987654321  ,  ",
            [123456789, 987654321],
            "Multiple empty entries",
            id="multiple_empty_entries",
        ),
    ],
)
def test_tester_ids_parsing_valid_inputs(
    input_value: str, expected_output: list[int], description: str
):
    """Test that valid tester ID strings are parsed correctly."""
    settings = AppSettings(testers_list=input_value)
    assert settings.tester_ids == expected_output, f"Failed for: {description}"


@pytest.mark.parametrize(
    "input_value,expected_output,description",
    [
        pytest.param("invalid", [], "Non-numeric value", id="non_numeric"),
        pytest.param(
            "123456789, invalid",
            [],
            "Mixed valid and invalid",
            id="mixed_valid_invalid",
        ),
        pytest.param("123456789.5", [], "Decimal number", id="decimal_number"),
        pytest.param(
            "123456789, 987654321invalid",
            [],
            "Number with trailing text",
            id="trailing_text",
        ),
        pytest.param(
            '"123456789", "invalid"',
            [],
            "Valid in quotes, invalid in quotes",
            id="quotes_mixed",
        ),
        pytest.param("not_a_number", [], "Completely invalid", id="completely_invalid"),
        pytest.param(
            "123456789, ",
            [123456789],
            "Trailing comma with space",
            id="trailing_comma_space",
        ),
    ],
)
def test_tester_ids_parsing_invalid_inputs(
    input_value: str, expected_output: list[int], description: str
):
    """Test that invalid tester ID strings return expected output."""
    settings = AppSettings(testers_list=input_value)
    assert settings.tester_ids == expected_output, (
        f"Should return {expected_output} for: {description}"
    )


def test_tester_ids_empty_config():
    """Test that empty/None testers_list returns empty list."""
    # Explicit empty string (avoiding any env var defaults)
    settings = AppSettings(testers_list="")
    assert settings.tester_ids == []


def test_tester_ids_preserves_order():
    """Test that the order of IDs is preserved."""
    input_value = "111, 222, 333, 444"
    expected = [111, 222, 333, 444]

    settings = AppSettings(testers_list=input_value)
    assert settings.tester_ids == expected


def test_tester_ids_handles_large_numbers():
    """Test that large integers (like Telegram user IDs) are handled correctly."""
    large_ids = "123456789, 2147483647, 9223372036854775807"
    expected = [123456789, 2147483647, 9223372036854775807]

    settings = AppSettings(testers_list=large_ids)
    assert settings.tester_ids == expected


def test_tester_ids_filters_empty_entries():
    """Test that empty entries from extra commas are filtered out."""
    input_value = "123456789,,987654321,,,"
    expected = [123456789, 987654321]

    settings = AppSettings(testers_list=input_value)
    assert settings.tester_ids == expected


def test_tester_ids_quote_removal_edge_cases():
    """Test edge cases for quote removal."""
    # Only opening quote
    settings = AppSettings(testers_list='"123456789, 987654321')
    assert settings.tester_ids == []  # Should fail parsing due to unmatched quote

    # Only closing quote
    settings = AppSettings(testers_list='123456789, 987654321"')
    assert settings.tester_ids == []  # Should fail parsing

    # Different quotes
    settings = AppSettings(testers_list="\"123456789, 987654321'")
    assert settings.tester_ids == []  # Mismatched quotes

    # Quotes in the middle (should not be removed)
    settings = AppSettings(testers_list='123456789, "987654321"')
    assert settings.tester_ids == []  # Should fail parsing due to quote in middle


def test_tester_ids_zero_and_negative():
    """Test handling of zero and negative numbers."""
    input_value = "0, -1, 123456789"
    expected = [0, -1, 123456789]

    settings = AppSettings(testers_list=input_value)
    assert settings.tester_ids == expected
