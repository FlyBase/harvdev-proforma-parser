def pytest_addoption(parser):
    parser.addoption("--config", action="store", dest='config')