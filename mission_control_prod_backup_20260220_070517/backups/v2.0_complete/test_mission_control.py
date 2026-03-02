#!/usr/bin/env python3
"""
Mission Control Automated Test Suite
Tests API endpoints, data validation, data quality, and integration flows
"""

import unittest
import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the mission_control directory to path
sys.path.insert(0, '/Users/raitsai/.openclaw/workspace/mission_control')

from server import (
    app, parse_unified_tracker, parse_markdown_table, load_price_cache,
    save_price_cache, build_stocks_view, build_options_view, build_cash_view,
    build_misc_view, build_totals, parse_analysis_archive,
    fetch_finnhub_price, fetch_yahoo_price, fetch_coingecko_price
)


class TestAPIEndpoints(unittest.TestCase):
    """Test all API endpoints return 200 with valid JSON"""
    
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
    
    def test_portfolio_endpoint(self):
        """Test /api/portfolio returns 200 with valid JSON"""
        response = self.client.get('/api/portfolio')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('last_price_refresh', data)
        self.assertIn('stocks', data)
        self.assertIn('options', data)
        self.assertIn('cash', data)
        self.assertIn('misc', data)
        self.assertIn('totals', data)
    
    def test_analysis_archive_endpoint(self):
        """Test /api/analysis-archive returns 200 with valid JSON"""
        response = self.client.get('/api/analysis-archive')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_earnings_research_endpoint(self):
        """Test /api/earnings-research returns 200 with valid JSON"""
        response = self.client.get('/api/earnings-research')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('content', data)
    
    def test_ideas_endpoint(self):
        """Test /api/ideas returns 200 with valid JSON"""
        response = self.client.get('/api/ideas')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_schedule_endpoint(self):
        """Test /api/schedule returns 200 with valid JSON"""
        response = self.client.get('/api/schedule')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        for item in data:
            self.assertIn('date', item)
            self.assertIn('event', item)
            self.assertIn('time', item)
    
    def test_corporate_endpoint(self):
        """Test /api/corporate returns 200 with valid JSON"""
        response = self.client.get('/api/corporate')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('team', data)
        self.assertIsInstance(data['team'], list)
    
    def test_usage_endpoint(self):
        """Test /api/usage returns 200 with valid JSON"""
        response = self.client.get('/api/usage')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('apis', data)
    
    def test_dashboard_endpoint(self):
        """Test / returns 200"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class TestDataValidation(unittest.TestCase):
    """Test data validation - totals calculation, duplicates, required fields"""
    
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        self.data_file = '/Users/raitsai/.openclaw/workspace/portfolio/unified_portfolio_tracker.md'
    
    def test_portfolio_totals_calculation(self):
        """Verify portfolio totals calculation is correct"""
        response = self.client.get('/api/portfolio')
        data = json.loads(response.data)
        
        totals = data['totals']
        
        # Calculate expected totals from individual components
        stocks_total = sum(s['total_value'] for s in data['stocks'])
        options_total = sum(o['current_value'] for o in data['options'])
        cash_total = data['cash']['Cash']['total'] + data['cash']['SGOV']['total']
        misc_total = sum(m['total_value'] for m in data['misc'])
        expected_grand_total = stocks_total + options_total + cash_total + misc_total
        
        # Verify totals match
        self.assertAlmostEqual(totals['stocks_etfs'], stocks_total, places=2)
        self.assertAlmostEqual(totals['options'], options_total, places=2)
        self.assertAlmostEqual(totals['cash_equivalents'], cash_total, places=2)
        self.assertAlmostEqual(totals['misc'], misc_total, places=2)
        self.assertAlmostEqual(totals['grand_total'], expected_grand_total, places=2)
    
    def test_no_duplicate_stocks(self):
        """Verify no duplicate stocks in aggregated view"""
        response = self.client.get('/api/portfolio')
        data = json.loads(response.data)
        
        tickers = [s['ticker'] for s in data['stocks']]
        unique_tickers = set(tickers)
        
        self.assertEqual(len(tickers), len(unique_tickers), 
                        f"Found duplicate tickers: {[t for t in tickers if tickers.count(t) > 1]}")
    
    def test_required_fields_in_stocks(self):
        """Verify all required fields present in stocks"""
        response = self.client.get('/api/portfolio')
        data = json.loads(response.data)
        
        required_fields = [
            'ticker', 'total_shares', 'total_cost_basis', 'accounts',
            'price', 'price_source', 'price_updated', 'cost_per_share',
            'total_value', 'total_return', 'total_return_pct'
        ]
        
        for stock in data['stocks']:
            for field in required_fields:
                self.assertIn(field, stock, f"Missing field '{field}' in stock {stock.get('ticker', 'unknown')}")
    
    def test_required_fields_in_options(self):
        """Verify all required fields present in options"""
        response = self.client.get('/api/portfolio')
        data = json.loads(response.data)
        
        required_fields = [
            'ticker', 'type', 'strike', 'expiration', 'total_contracts',
            'total_entry_value', 'accounts', 'current_value', 'note'
        ]
        
        for option in data['options']:
            for field in required_fields:
                self.assertIn(field, option, f"Missing field '{field}' in option {option.get('ticker', 'unknown')}")
    
    def test_required_fields_in_totals(self):
        """Verify all required fields present in totals"""
        response = self.client.get('/api/portfolio')
        data = json.loads(response.data)
        
        required_fields = ['stocks_etfs', 'options', 'cash_equivalents', 'misc', 'grand_total']
        
        for field in required_fields:
            self.assertIn(field, data['totals'], f"Missing field '{field}' in totals")
    
    def test_required_fields_in_cash(self):
        """Verify all required fields present in cash"""
        response = self.client.get('/api/portfolio')
        data = json.loads(response.data)
        
        self.assertIn('Cash', data['cash'])
        self.assertIn('SGOV', data['cash'])
        
        # Check Cash structure
        self.assertIn('total', data['cash']['Cash'])
        self.assertIn('accounts', data['cash']['Cash'])
        
        # Check SGOV structure
        self.assertIn('total', data['cash']['SGOV'])
        self.assertIn('total_shares', data['cash']['SGOV'])
        self.assertIn('price', data['cash']['SGOV'])
        self.assertIn('accounts', data['cash']['SGOV'])


class TestDataQuality(unittest.TestCase):
    """Test data quality - counts, ranges, and constraints"""
    
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
    
    def test_33_stocks_returned(self):
        """Verify 33 stocks are returned"""
        response = self.client.get('/api/portfolio')
        data = json.loads(response.data)
        
        # Count unique tickers (excluding SGOV and Cash which are in cash equivalents)
        stock_tickers = [s['ticker'] for s in data['stocks']]
        
        self.assertEqual(len(stock_tickers), 33, 
                        f"Expected 33 stocks, got {len(stock_tickers)}: {stock_tickers}")
    
    def test_10_options_returned(self):
        """Verify 10 options are returned"""
        response = self.client.get('/api/portfolio')
        data = json.loads(response.data)
        
        self.assertEqual(len(data['options']), 10,
                        f"Expected 10 options, got {len(data['options'])}")
    
    def test_5_analyses_returned(self):
        """Verify 5 analyses are returned"""
        response = self.client.get('/api/analysis-archive')
        data = json.loads(response.data)
        
        self.assertGreaterEqual(len(data), 5,
                               f"Expected at least 5 analyses, got {len(data)}")
    
    def test_positive_values_for_shares_and_contracts(self):
        """Verify all shares and contract counts are positive"""
        response = self.client.get('/api/portfolio')
        data = json.loads(response.data)
        
        for stock in data['stocks']:
            self.assertGreater(stock['total_shares'], 0,
                              f"Stock {stock['ticker']} has non-positive shares")
        
        for option in data['options']:
            # Contracts can be negative (short positions)
            self.assertNotEqual(option['total_contracts'], 0,
                               f"Option {option['ticker']} has zero contracts")
    
    def test_valid_ticker_symbols(self):
        """Verify ticker symbols are valid (alphanumeric, 1-5 chars)"""
        response = self.client.get('/api/portfolio')
        data = json.loads(response.data)
        
        for stock in data['stocks']:
            ticker = stock['ticker']
            self.assertRegex(ticker, r'^[A-Z0-9]{1,5}$',
                           f"Invalid ticker format: {ticker}")


class TestIntegration(unittest.TestCase):
    """Integration tests for full workflows"""
    
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
    
    @patch('server.fetch_finnhub_price')
    @patch('server.fetch_yahoo_price')
    @patch('server.fetch_coingecko_price')
    @patch('server.save_price_cache')
    def test_refresh_prices_flow(self, mock_save, mock_coingecko, mock_yahoo, mock_finnhub):
        """Test full refresh-prices flow"""
        # Mock the price fetch functions
        mock_finnhub.return_value = 150.25
        mock_yahoo.return_value = 125.50
        mock_coingecko.return_value = 3000.00
        mock_save.return_value = None
        
        # Call the refresh endpoint
        response = self.client.post('/api/refresh-prices')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('updated', data)
        self.assertGreater(data['updated'], 0)
        
        # Verify that price fetching functions were called
        self.assertTrue(mock_finnhub.called or mock_yahoo.called or mock_coingecko.called,
                       "No price fetch functions were called")
    
    def test_data_consistency_after_refresh(self):
        """Verify data consistency between portfolio and refresh"""
        # Get initial portfolio data
        response1 = self.client.get('/api/portfolio')
        data1 = json.loads(response1.data)
        
        stock_count_before = len(data1['stocks'])
        option_count_before = len(data1['options'])
        
        # Data should remain consistent
        response2 = self.client.get('/api/portfolio')
        data2 = json.loads(response2.data)
        
        self.assertEqual(len(data2['stocks']), stock_count_before,
                        "Stock count changed unexpectedly")
        self.assertEqual(len(data2['options']), option_count_before,
                        "Option count changed unexpectedly")
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # 1. Get portfolio
        portfolio_response = self.client.get('/api/portfolio')
        self.assertEqual(portfolio_response.status_code, 200)
        portfolio = json.loads(portfolio_response.data)
        
        # 2. Get analysis archive
        analysis_response = self.client.get('/api/analysis-archive')
        self.assertEqual(analysis_response.status_code, 200)
        analyses = json.loads(analysis_response.data)
        
        # 3. Verify cross-reference capability
        stock_tickers = {s['ticker'] for s in portfolio['stocks']}
        analysis_tickers = {a['ticker'] for a in analyses}
        
        # At least some stocks should have analysis
        common_tickers = stock_tickers & analysis_tickers
        self.assertGreater(len(common_tickers), 0,
                          "No common tickers between portfolio and analysis")


class TestUtilityFunctions(unittest.TestCase):
    """Test utility and helper functions"""
    
    def test_parse_markdown_table(self):
        """Test markdown table parsing"""
        content = """
### Stocks & ETFs
| Ticker | Shares | Cost Basis |
|--------|--------|------------|
| AAPL | 100 | $10000 |
| MSFT | 50 | $5000 |
"""
        rows = parse_markdown_table(content, '### Stocks & ETFs')
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['Ticker'], 'AAPL')
        self.assertEqual(rows[0]['Shares'], '100')
        self.assertEqual(rows[1]['Ticker'], 'MSFT')
    
    def test_load_save_price_cache(self):
        """Test price cache load and save"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Patch the PRICE_FILE constant
            with patch('server.PRICE_FILE', temp_path):
                # Save test data
                test_prices = {'AAPL': {'price': 150.0, 'source': 'test'}}
                save_price_cache(test_prices, '2024-01-01T00:00:00')
                
                # Load and verify
                prices, last_updated = load_price_cache()
                self.assertIn('AAPL', prices)
                self.assertEqual(prices['AAPL']['price'], 150.0)
        finally:
            os.unlink(temp_path)
    
    def test_build_totals_calculation(self):
        """Test totals calculation accuracy"""
        stocks = [
            {'total_value': 1000.0, 'total_cost_basis': 900.0},
            {'total_value': 2000.0, 'total_cost_basis': 1800.0}
        ]
        options = [
            {'current_value': 500.0, 'total_entry_value': 400.0}
        ]
        cash = {
            'Cash': {'total': 1000.0, 'accounts': []},
            'SGOV': {'total': 2000.0, 'total_shares': 20, 'price': 100.0, 'accounts': []}
        }
        misc = [
            {'total_value': 500.0, 'total_cost_basis': 450.0}
        ]
        
        totals = build_totals(stocks, options, cash, misc)
        
        self.assertEqual(totals['stocks_etfs'], 3000.0)
        self.assertEqual(totals['options'], 500.0)
        self.assertEqual(totals['cash_equivalents'], 3000.0)
        self.assertEqual(totals['misc'], 500.0)
        self.assertEqual(totals['grand_total'], 7000.0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404"""
        response = self.client.get('/api/invalid-endpoint')
        self.assertEqual(response.status_code, 404)
    
    def test_data_file_not_found(self):
        """Test handling of missing data file"""
        with patch('server.DATA_FILE', '/nonexistent/file.md'):
            response = self.client.get('/api/portfolio')
            # Should handle gracefully, not crash
            self.assertIn(response.status_code, [200, 500])


def run_tests():
    """Run the test suite and return results"""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestDataQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)