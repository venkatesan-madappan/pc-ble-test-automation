import unittest
import logging

from .config_setup import Settings

def test_suite():
    logger.info("Test Suite Invoking")
    suite = unittest.TestSuite()
    suite.addTest(load_suite_adn_setup_validation.test_suite())
    return suite


if __name__ == '__main__':
    logger.info("Are we here")
    asdfsdf
    #logging.basicConfig(level=Settings.current().loglevel)
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(defaultTest='test_suite', argv=Settings.clean_args())
