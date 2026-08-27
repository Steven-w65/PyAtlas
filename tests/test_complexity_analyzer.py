from analyzer.complexity_analyzer import ComplexityAnalyzer


def test_trivial_function_has_low_complexity() -> None:
    values = ComplexityAnalyzer().function_complexities(
        "def straight_line():\n    value = 1\n    return value\n",
    )

    assert values["straight_line"] == 1


def test_branching_increases_complexity() -> None:
    analyzer = ComplexityAnalyzer()
    simple = analyzer.function_complexities("def choose(value):\n    return value\n")
    branching = analyzer.function_complexities(
        "def choose(value):\n"
        "    if value > 10:\n"
        "        return 2\n"
        "    if value > 0:\n"
        "        return 1\n"
        "    return 0\n",
    )

    assert simple["choose"] < branching["choose"]


def test_method_uses_qualified_name() -> None:
    values = ComplexityAnalyzer().function_complexities(
        "class Worker:\n"
        "    def run(self, ready):\n"
        "        if ready:\n"
        "            return True\n"
        "        return False\n",
    )

    assert values == {"Worker.run": 2}


def test_maintainability_index_is_numeric_for_valid_source() -> None:
    value = ComplexityAnalyzer().maintainability_index(
        "def straight_line():\n    return 1\n",
    )

    assert isinstance(value, float)
    assert 0 <= value <= 100


def test_malformed_source_returns_safe_values() -> None:
    analyzer = ComplexityAnalyzer()

    assert analyzer.function_complexities("def broken(:\n") == {}
    assert analyzer.maintainability_index("def broken(:\n") is None
