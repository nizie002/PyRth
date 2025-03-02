import unittest


def temperature_prediction_assertions(
    test_case: unittest.TestCase, module: object
) -> None:
    # Assert that temperature prediction-specific attributes are present
    test_case.assertTrue(
        hasattr(module, "predicted_temperature"),
        "Missing predicted_temperature attribute",
    )
    test_case.assertTrue(
        hasattr(module, "power_function_int"), "Missing power_function_int attribute"
    )
    test_case.assertTrue(
        hasattr(module, "impulse_response_int"),
        "Missing impulse_response_int attribute",
    )
    test_case.assertIn(
        "prediction", module.data_handlers, "Missing 'prediction' in data_handlers"
    )
