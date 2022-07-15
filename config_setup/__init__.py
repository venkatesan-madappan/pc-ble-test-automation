import sys
import logging

class Settings(object):
    settings = None
    CFG_TAG = 1
    def __init__(self, serial_ports, number_of_iterations, log_level, driver_log_level, baud_rate, \
                 retransmission_interval, response_timeout, mtu, nrf_family, test_output_directory):
        #logger.info("Setting Constructor")
        self.serial_ports = serial_ports
        self.number_of_iterations = number_of_iterations
        self.log_level = getattr(logging, log_level.upper(), None)
        self.driver_log_level = driver_log_level
        self.baud_rate = baud_rate
        self.retransmission_interval = retransmission_interval
        self.response_timeout = response_timeout
        self.mtu = mtu
        self.nrf_family = nrf_family
        self.test_output_directory = test_output_directory

    @classmethod
    def current(cls):
        if cls.settings is None:
            cls.configure_default_args()
            #pass
        return cls.settings

    @staticmethod
    def clean_args():
        print("Clean Arguments")

    @classmethod
    def configure_default_args(cls):
        nrf_family = "NRF52"
        serial_ports = ["COM4", "COM18"]
        log_level = "info"
        baud_rate = 1000000
        retransmission_interval = 300
        mtu = 150
        iterations = 1
        response_timeout = 1500
        driver_log_level = "info"
        test_output_directory = "test-reports"
        cls.settings = Settings(serial_ports, iterations, log_level, driver_log_level, baud_rate, \
                                retransmission_interval, response_timeout, mtu, nrf_family, test_output_directory)

from pc_ble_driver_py import config

config.__conn_ic_id__ = Settings.current().nrf_family

from pc_ble_driver_py.ble_adapter import BLEAdapter

from pc_ble_driver_py.ble_driver import (
    BLEDriver,
    BLEAdvData,
    BLEEvtID,
    BLEEnableParams,
    BLEGapTimeoutSrc,
    BLEUUID,
    BLEConfigCommon,
    BLEConfig,
    BLEConfigConnGatt,
)

from .initialize import initialize_adapter, open_adapter

__all__ = [
    "config",
    "BLEDriver",
    "BLEAdvData",
    "BLEEvtID",
    "BLEEnableParams",
    "BLEGapTimeoutSrc",
    "BLEUUID",
    "BLEConfigCommon",
    "BLEConfig",
    "BLEConfigConnGatt",
    "BLEAdapter",
    "Settings",
    "initialize_adapter",
    "open_adapter",
]
