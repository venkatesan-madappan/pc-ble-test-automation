from config_setup import *
import logging
logger = logging.getLogger(__name__)
import time
import unittest
import xmlrunner

from pc_ble_driver_py.ble_driver import (
    BLEAdvData,
    BLEConfig,
    BLEConfigConnGatt,
    BLEDriver,
    BLEEnableParams,
    BLEConfigConnGap,
)
from pc_ble_driver_py.observers import BLEAdapterObserver, BLEDriverObserver


class Peripheral(BLEDriverObserver, BLEAdapterObserver):
    def __init__(self, adapter):
        self.adapter = adapter
        logger.info(
            "Peripheral adapter is %d",
            self.adapter.driver.rpc_adapter.internal,
        )

        self.adapter.observer_register(self)
        self.adapter.driver.observer_register(self)
        self.mtu_req = None

    def start(self, adv_name):
        adv_data = BLEAdvData(complete_local_name=adv_name)
        self.adapter.driver.ble_gap_adv_data_set(adv_data)
        self.adapter.driver.ble_gap_adv_start(tag=Settings.CFG_TAG)

class Advertise(unittest.TestCase):
    def setUp(self):
        self.settings = Settings.current()

    def test_setup_validation(self):
        self.adapter = initialize_adapter(self.settings.serial_ports[0], self.settings.baud_rate, \
                                          self.settings.retransmission_interval, \
                                          self.settings.response_timeout, self.settings.driver_log_level)
        peripheral = Peripheral(self.adapter)

        peripheral.start("Venkat-pc-ble-api")
        time.sleep(1)
        peripheral.adapter.close()

    def tearDown(self):
        logger.debug("Tear Down")
        pass


if __name__ == '__main__':
    logging.basicConfig(
        level=Settings.current().log_level,
        format="%(asctime)s [%(thread)d/%(threadName)s] %(message)s",
    )
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(
            output=Settings.current().test_output_directory
        ),
        argv=Settings.clean_args(),
    )
