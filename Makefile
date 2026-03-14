.PHONY: test test-auth test-customers test-products test-invoices test-payments test-reports test-all test-coverage test-html test-negative help install

# Install test dependencies
install:
	pip install -r tests/requirements.txt

# Run all tests
test:
	pytest tests/ -v

# Run specific test modules
test-auth:
	pytest tests/test_auth.py -v

test-customers:
	pytest tests/test_customers.py -v

test-products:
	pytest tests/test_products.py -v

test-invoices:
	pytest tests/test_invoices.py -v

test-payments:
	pytest tests/test_payments.py -v

test-reports:
	pytest tests/test_reports.py -v

# Run all tests with markers
test-all:
	pytest tests/ -v -m "auth or customers or products or invoices or payments or reports"

# Run tests with coverage report
test-coverage:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run tests with HTML report
test-html:
	pytest tests/ -v --html=report.html --self-contained-html

# Run negative/error tests only
test-negative:
	pytest tests/ -v -m negative

# Run single test
test-single:
	@echo "Usage: make test-single TEST=tests/test_auth.py::test_login_user_success"
	pytest $(TEST) -v -s

# Stop on first failure
test-fail-fast:
	pytest tests/ -v -x

# Show test collection only (no execution)
test-collect:
	pytest tests/ --collect-only

# Help
help:
	@echo "Viyapar API Test Suite - Available Commands:"
	@echo ""
	@echo "  make install              - Install test dependencies"
	@echo "  make test                 - Run all tests"
	@echo "  make test-auth            - Run only auth tests"
	@echo "  make test-customers       - Run only customer tests"
	@echo "  make test-products        - Run only product tests"
	@echo "  make test-invoices        - Run only invoice tests"
	@echo "  make test-payments        - Run only payment tests"
	@echo "  make test-reports         - Run only report tests"
	@echo "  make test-all             - Run all tests with markers"
	@echo "  make test-coverage        - Run tests with coverage report"
	@echo "  make test-html            - Run tests with HTML report"
	@echo "  make test-negative        - Run only negative tests"
	@echo "  make test-single TEST=... - Run single test"
	@echo "  make test-fail-fast       - Stop on first failure"
	@echo "  make test-collect         - Show test collection only"
	@echo ""
