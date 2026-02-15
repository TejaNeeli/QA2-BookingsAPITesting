import pytest
import logging
import os

LOG_PATH = os.path.join(os.path.dirname(__file__), 'logfile.log')

class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    # Set up logging with timestamp for all tests
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = FlushFileHandler(LOG_PATH, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    setattr(config.option, "htmlpath", r'C:\Users\neteja\PycharmProjects\AITOOL\Api_Automation\Reports\Report.html')
    setattr(config.option, "self_contained_html", True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    if report.when == 'call' or report.when == "setup":
        xfail = hasattr(report, 'wasxfail')
        log_path = LOG_PATH
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            if pytest_html is not None:
                extra.append(pytest_html.extras.text(log_content, name='Log File'))
        except Exception:
            pass
        report.extra = extra
