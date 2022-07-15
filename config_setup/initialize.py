from pc_ble_driver_py.ble_driver import (
    BLEDriver,
    BLEEnableParams,
    BLEConfig,
    BLEConfigConnGatt,
    BLEConfigConnGap,
)
from pc_ble_driver_py.ble_adapter import BLEAdapter
from . import Settings

def initialize_adapter(port, baud_rate, retransmission_interval, response_timeout, driver_log_level,\
                       only_initialize=False):
    settings = Settings.current()

    driver = BLEDriver(serial_port=port, auto_flash=False, baud_rate=baud_rate, \
                       retransmission_interval=retransmission_interval, response_timeout=response_timeout, \
                       log_severity_level=driver_log_level)
    adapter = BLEAdapter(driver)
    adapter.default_mtu = settings.mtu

    if not only_initialize:
        open_adapter(settings, adapter)

    return adapter


def open_adapter(settings, adapter):
    adapter.open()
    if settings.nrf_family == "NRF51":
        assert True, "Sorry this Board is not supported"
    elif settings.nrf_family == "NRF52":
        gatt_cfg = BLEConfigConnGatt()
        gatt_cfg.att_mtu = adapter.default_mtu
        gatt_cfg.tag = Settings.CFG_TAG
        adapter.driver.ble_cfg_set(BLEConfig.conn_gatt, gatt_cfg)
        if hasattr(settings, "event_length"):
            gap_cfg = BLEConfigConnGap()
            gap_cfg.event_length = settings.event_length
            adapter.driver.ble_cfg_set(BLEConfig.conn_gap, gap_cfg)

        adapter.driver.ble_enable()
    return

