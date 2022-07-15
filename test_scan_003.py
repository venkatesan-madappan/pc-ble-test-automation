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


class Central(BLEDriverObserver, BLEAdapterObserver):
    def __init__(self, adapter):
        self.adapter = adapter
        logger.info(
            "Central adapter is %d",
            self.adapter.driver.rpc_adapter.internal,
        )
        self.adapter.observer_register(self)
        self.adapter.driver.observer_register(self)
        self.adv_received = False

    def start(self):
        print("Going to scan the ADV Data")
        self.adapter.driver.ble_gap_scan_start()

    def on_gap_evt_adv_report(self, ble_driver, conn_handle, peer_addr, rssi, adv_type, adv_data):
        if BLEAdvData.Types.complete_local_name in adv_data.records:
            dev_name_list = adv_data.records[BLEAdvData.Types.complete_local_name]
        elif BLEAdvData.Types.short_local_name in adv_data.records:
            dev_name_list = adv_data.records[BLEAdvData.Types.short_local_name]
        else:
            return

        dev_name = "".join(chr(e) for e in dev_name_list)
        address_string = "".join("{0:02X}".format(b) for b in peer_addr.addr)
        logger.info(
            "Received advertisment report, address: 0x%s, device_name: %s",
            address_string,
            dev_name,)
        self.adv_received = True


class Scan(unittest.TestCase):
    def setUp(self):
        self.settings = Settings.current()
        self.adapter = initialize_adapter(self.settings.serial_ports[0], self.settings.baud_rate, \
                                          self.settings.retransmission_interval, \
                                          self.settings.response_timeout, self.settings.driver_log_level,\
                                          only_initialize=True)
        logger.info("Iam validating here")

    def test_scan(self):

        self.central = Central(self.adapter)

        for _ in range(0, self.settings.number_of_iterations):
            open_adapter(self.settings, self.adapter)
            self.central.start()
            time.sleep(2)
            self.assertTrue(self.central.adv_received)
            self.adapter.close()

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
