import numpy as np
from data.measurement_data import (
    MOSFET_DRY_DATA,
    MOSFET_TIM_DATA,
    MOSFET_CALIB_DATA,
    TEMP_DATA,
)
from parameterized import parameterized
from test_transient_base import TransientTestBase
from assertions.standard_assertions import standard_assertions

test_cases_basic = [
    {
        "name": "MOSFET_dry_basic_fft",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSFET_dry_basic_fft",
            "bayesian": False,
            "conv_mode": "volt",
            "filter_name": "hann",
            "filter_range": 0.90,
            "filter_parameter": 0.0,
            "pad_factor_pre": 0.15,
            "pad_factor_after": 0.15,
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": "MOSFET_tim_basic_bayesian",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSFET_tim_basic_bayesian",
            "conv_mode": "volt",
            "bayesian": True,
            "bay_steps": 1000,
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": "MOSFET_tim_basic_polylong",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSFET_tim_basic_polylong",
            "conv_mode": "volt",
            "bayesian": True,
            "bay_steps": 1000,
            "struc_method": "polylong",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": "MOSFET_tim_basic_khatwani",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSFET_tim_basic_khatwani",
            "conv_mode": "volt",
            "bayesian": True,
            "bay_steps": 1000,
            "struc_method": "khatwani",
            "log_time_size": 75,
            "precision": 3600,
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": "MOSFET_tim_basic_sobhy",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSFET_tim_basic_sobhy",
            "conv_mode": "volt",
            "bayesian": True,
            "bay_steps": 1000,
            "struc_method": "sobhy",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": "MOSFET_tim_basic_boor_golub",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSFET_tim_basic_boor_golub",
            "conv_mode": "volt",
            "bayesian": True,
            "bay_steps": 1000,
            "struc_method": "boor_golub",
            "log_time_size": 75,
            "precision": 2000,
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": "MOSFET_tim_basic_lanczos",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSFET_tim_basic_lanczos",
            "conv_mode": "volt",
            "bayesian": True,
            "bay_steps": 1000,
            "struc_method": "lanczos",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": "temp_transient",
        "params": {
            "data": TEMP_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "TEMP_DATA",
            "conv_mode": "temp",
            "extrapolate": False,
            "data_cut_lower": 242,
            "data_cut_upper": float("inf"),
            "temp_0_avg_range": (230, 241),
        },
    },
    {
        "name": "T3ster_basic_1",
        "params": {
            "infile": "tests/data/t3ster/T25_I-m5m-I-h600m_100s.raw",
            "infile_pwr": "tests/data/t3ster/T25_I-m5m-I-h600m_100s.pwr",
            "infile_tco": "tests/data/t3ster/calib.tco",
            "output_dir": "tests/output/basic_test",
            "label": "t3ster_basic_1",
            "conv_mode": "t3ster",
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": "T3ster_basic_2",
        "params": {
            "infile": "tests/data/t3ster/T25_I-m5m-I-h600m_100s_2.raw",
            "infile_pwr": "tests/data/t3ster/T25_I-m5m-I-h600m_100s_2.pwr",
            "infile_tco": "tests/data/t3ster/calib.tco",
            "output_dir": "tests/output/basic_test",
            "label": "t3ster_basic_2",
            "conv_mode": "t3ster",
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
]


class TestStandardModule(TransientTestBase):
    test_cases = test_cases_basic

    @parameterized.expand([(case["name"], case["params"]) for case in test_cases])
    def test_standard_module(self, name: str, params: dict):
        # 'standard_module' is the evaluation method specific to standard tests.
        self._run_evaluation_test(
            name,
            params,
            evaluation_module="standard_module",
            additional_assertions=standard_assertions,
        )
