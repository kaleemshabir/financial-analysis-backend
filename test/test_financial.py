import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from main import app
from routers.auth import get_current_user
from models import Company, FinancialData

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database and tables
Base.metadata.create_all(bind=engine)

# Test client
client = TestClient(app)

# Mock current user for authentication
def override_get_current_user():
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "role": "admin",
        "is_active": True
    }

# Apply the mock to our endpoints
app.dependency_overrides[get_current_user] = override_get_current_user

# Test data
test_company = {
    "name": "Test Company"
}

test_financial_data = {
    "fiscal_year": "2023",
    "prepared_by": "Test User",
    "notes": "Test financial data",
    "total_revenue": 1000000.0,
    "gross_profit": 500000.0,
    "operating_profit": 300000.0,
    "net_income": 200000.0,
    "number_of_shares": 1000000.0,
    "eps_high": 0.25,
    "eps_low": 0.15,
    "earning_power": 0.2,
    "free_cash_flow": 150000.0,
    "total_assets": 2000000.0,
    "total_liabilities": 800000.0,
    "shareholders_equity": 1200000.0,
    "current_assets": 600000.0,
    "current_liabilities": 400000.0,
    "dividends_per_share": 0.05,
    "dividend_rate": 2.5
}

# Tests
def test_create_company():
    response = client.post("/financial/companies/", json=test_company)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_company["name"]
    assert "id" in data
    return data["id"]

def test_create_financial_data():
    # First create a company
    company_id = test_create_company()
    
    # Then create financial data for this company
    response = client.post(
        f"/financial/companies/{company_id}/financial-data/",
        json=test_financial_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["fiscal_year"] == test_financial_data["fiscal_year"]
    assert data["total_revenue"] == test_financial_data["total_revenue"]
    assert data["company_id"] == company_id

def test_get_financial_data_by_company():
    # First create a company and financial data
    company_id = test_create_company()
    client.post(
        f"/financial/companies/{company_id}/financial-data/",
        json=test_financial_data
    )
    
    # Then get financial data for this company
    response = client.get(f"/financial/companies/{company_id}/financial-data/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["fiscal_year"] == test_financial_data["fiscal_year"]

def test_get_financial_data_by_year():
    # First create a company and financial data
    company_id = test_create_company()
    client.post(
        f"/financial/companies/{company_id}/financial-data/",
        json=test_financial_data
    )
    
    # Then get financial data for this company and fiscal year
    response = client.get(
        f"/financial/companies/{company_id}/financial-data/{test_financial_data['fiscal_year']}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["fiscal_year"] == test_financial_data["fiscal_year"]
    assert data["total_revenue"] == test_financial_data["total_revenue"]

def test_duplicate_financial_data():
    # First create a company and financial data
    company_id = test_create_company()
    client.post(
        f"/financial/companies/{company_id}/financial-data/",
        json=test_financial_data
    )
    
    # Try to create duplicate financial data for the same company and fiscal year
    response = client.post(
        f"/financial/companies/{company_id}/financial-data/",
        json=test_financial_data
    )
    assert response.status_code == 400  # Bad request - duplicate data 