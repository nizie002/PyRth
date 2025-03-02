import unittest


def comparison_assertions(test_case: unittest.TestCase, module: object) -> None:
    # Assert that comparison-specific attributes are present and non-empty
    test_case.assertTrue(
        hasattr(module, "time_const_comparison"),
        "Missing time_const_comparison attribute",
    )
    test_case.assertTrue(
        hasattr(module, "structure_comparison"),
        "Missing structure_comparison attribute",
    )
    test_case.assertTrue(
        hasattr(module, "total_resist_diff"), "Missing total_resist_diff attribute"
    )
    test_case.assertIn(
        "comparison", module.data_handlers, "Missing 'comparison' in data_handlers"
    )
    test_case.assertGreater(
        len(module.time_const_comparison), 0, "Empty time_const_comparison"
    )
    test_case.assertGreater(
        len(module.structure_comparison), 0, "Empty structure_comparison"
    )
    test_case.assertGreater(len(module.total_resist_diff), 0, "Empty total_resist_diff")
