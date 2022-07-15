from config_setup import *
import logging
logger = logging.getLogger(__name__)
import time
import unittest
import xmlrunner
from queue import Queue

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
        self.conn_q = Queue()
        self.adapter.observer_register(self)
        self.adapter.driver.observer_register(self)
        self.mtu_req = None

    def start(self, adv_name):
        adv_data = BLEAdvData(complete_local_name=adv_name)
        self.adapter.driver.ble_gap_adv_data_set(adv_data)
        self.adapter.driver.ble_gap_adv_start(tag=Settings.CFG_TAG)

    def on_gap_evt_connected(self, ble_driver, conn_handle, peer_addr, \
                             role, conn_params):
        self.conn_q.put(conn_handle)
        logger.info("Peripheral : Connection Successful")


class Central(BLEDriverObserver, BLEAdapterObserver):
    def __init__(self, adapter, connect_with):
        self.adapter = adapter
        self.connect_with = connect_with
        logger.info(
            "Central adapter is %d",
            self.adapter.driver.rpc_adapter.internal,
        )
        self.conn_q = Queue()
        self.adapter.observer_register(self)
        self.adapter.driver.observer_register(self)
        self.conn_handle = None
        self.adv_received = False

    def start(self):
        print("Going to scan the ADV Data")
        self.adapter.driver.ble_gap_scan_start()
        #self.conn_handle = self.conn_q.get(timeout=5)

    def stop(self):
        if self.conn_handle:
            self.adapter.driver.ble_gap_disconnect(self.conn_handle)
            logger.info("GAP Disconnected")

    def on_gap_evt_adv_report(self, ble_driver, conn_handle, peer_addr, rssi, adv_type, adv_data):
        if BLEAdvData.Types.complete_local_name in adv_data.records:
            dev_name_list = adv_data.records[BLEAdvData.Types.complete_local_name]
        elif BLEAdvData.Types.short_local_name in adv_data.records:
            dev_name_list = adv_data.records[BLEAdvData.Types.short_local_name]
        else:
            return

        dev_name = "".join(chr(e) for e in dev_name_list)
        address_string = "".join("{0:02X}".format(b) for b in peer_addr.addr)

        if dev_name == self.connect_with:
            logger.info(
                "Received advertisment report, address: 0x%s, device_name: %s",
                address_string,
                dev_name,)
            self.adapter.connect(peer_addr, tag=Settings.CFG_TAG)
        else:
            logger.info("Device Name Miss : %s", dev_name)
            pass

        logger.info("Received advertisment report, address: 0x%s, \
        device_name: %s",address_string, dev_name,)
        self.adv_received = True

    def on_gap_evt_connected(self, ble_driver, conn_handle, peer_addr, \
                             role, conn_params):
        self.conn_q.put(conn_handle)
        logger.info("Central : Connection Successful")

class Connect(unittest.TestCase):
    def setUp(self):
        self.settings = Settings.current()
        self.p_adapter = initialize_adapter(self.settings.serial_ports[0], self.settings.baud_rate, \
                                          self.settings.retransmission_interval, \
                                          self.settings.response_timeout, self.settings.driver_log_level)
        self.c_adapter = initialize_adapter(self.settings.serial_ports[1], self.settings.baud_rate, \
                                          self.settings.retransmission_interval, \
                                          self.settings.response_timeout, self.settings.driver_log_level,\
                                          only_initialize=True)

    def test_connect(self):

        self.peripheral = Peripheral(self.p_adapter)

        self.peripheral.start("Venkat-pc-ble-api")

        time.sleep(2)

        self.central = Central(self.c_adapter, "Venkat-pc-ble-api")

        for i in range(0, self.settings.number_of_iterations):
            print("attempt :",i)
            open_adapter(self.settings, self.c_adapter)
            self.central.start()
            time.sleep(2)
            self.assertTrue(self.central.adv_received)
            self.c_adapter.close()

        time.sleep(2)

        self.assertFalse(self.central.conn_q.empty(), "Centrial Connection Event failed")
        self.assertFalse(self.peripheral.conn_q.empty(), "Centrial Connection Event failed")

    def tearDown(self):
        logger.debug("Tear Down")
        self.p_adapter.close()
        self.central.stop()

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
