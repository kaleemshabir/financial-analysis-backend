from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict
from database import SessionLocal
from models import Company, FinancialData
from .auth import get_current_user
from pydantic import BaseModel, Field, field_validator


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models for request and response
class CompanyBase(BaseModel):
    name: str


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int

    class Config:
        from_attributes = True


class FinancialDataBase(BaseModel):
    fiscal_year: str
    prepared_by: Optional[str] = None
    notes: Optional[str] = None
    
    # Income Accounts Analysis
    total_revenue: float = Field(..., gt=0)
    # revenue_yoy_change: Optional[float] = None
    gross_profit: float
    gross_profit_margin: Optional[float] = None
    # gross_profit_yoy_change: Optional[float] = None
    operating_profit: float
    operating_profit_margin: Optional[float] = None
    # operating_profit_yoy_change: Optional[float] = None
    net_profit: float
    net_profit_margin: Optional[float] = None
    # net_profit_yoy_change: Optional[float] = None
    number_of_shares: float = Field(..., gt=0)
    eps: float
    price_high: float
    price_low: float
    earning_power: Optional[float] = None
    free_cash_flow: float
    # free_cash_flow_yoy_change: Optional[float] = None
    # book_value_yoy_change: Optional[float] = None
    
    # Assets Accounts Analysis
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    return_on_invested_capital: Optional[float] = None
    book_value: Optional[float] = None
    book_value_per_share: Optional[float] = None
    current_ratio: Optional[float] = None
    
    # Dividends Accounts Analysis
    dividends_per_share: float
    dividend_rate: float
    
    @field_validator('fiscal_year')
    def validate_fiscal_year(cls, v):
        # Simple validation to ensure fiscal_year is a valid year format
        try:
            year = int(v)
            if year < 1900 or year > 2100:
                raise ValueError('Year must be between 1900 and 2100')
        except ValueError:
            raise ValueError('Fiscal year must be a valid year')
        return v


class FinancialDataCreate(FinancialDataBase):
    pass


class FinancialDataResponse(FinancialDataBase):
    id: int
    company_id: int
    # Include YoY fields in response
    revenue_yoy_change: Optional[float] = None
    gross_profit_margin: Optional[float] = None
    gross_profit_yoy_change: Optional[float] = None
    operating_profit_margin: Optional[float] = None
    operating_profit_yoy_change: Optional[float] = None
    net_profit_margin: Optional[float] = None
    net_profit_yoy_change: Optional[float] = None
    free_cash_flow_yoy_change: Optional[float] = None
    book_value_yoy_change: Optional[float] = None

    class Config:
        from_attributes = True


# New response model for dashboard data
class FinancialMetric(BaseModel):
    year: str
    revenue: float
    revenue_yoy_change: Optional[float] = None
    gross_profit: float
    gross_profit_margin: Optional[float] = None
    gross_profit_yoy_change: Optional[float] = None
    operating_profit: float
    operating_profit_margin: Optional[float] = None
    operating_profit_yoy_change: Optional[float] = None
    net_profit: float
    net_profit_margin: Optional[float] = None
    net_profit_yoy_change: Optional[float] = None
    free_cash_flow: float
    free_cash_flow_yoy_change: Optional[float] = None
    number_of_shares: float
    
    # Calculated ratios
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    return_on_invested_capital: Optional[float] = None
    book_value: Optional[float] = None
    book_value_per_share: Optional[float] = None
    book_value_yoy_change: Optional[float] = None
    current_ratio: Optional[float] = None
    eps: Optional[float] = None
    price_high: Optional[float] = None
    price_low: Optional[float] = None
    earning_power: Optional[float] = None
    dividends_per_share: Optional[float] = None
    dividend_rate: Optional[float] = None
    
    # YoY changes
    yoy: Dict[str, Optional[float]]

    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    company: str
    metrics: List[FinancialMetric]


def calculate_financial_metrics(financial_data_list: List[FinancialData], company_name: str) -> Dict:
    """
    Calculate financial metrics and year-over-year changes from raw financial data
    
    Args:
        financial_data_list: List of FinancialData objects sorted by fiscal_year
        company_name: Name of the company
        
    Returns:
        Dictionary with company name and metrics
    """
    if not financial_data_list:
        return {"company": company_name, "metrics": []}
    
    # Sort data by fiscal year (convert to string for comparison)
    sorted_data = sorted(financial_data_list, key=lambda x: str(x.fiscal_year))
    metrics = []
    
    # Previous year data for YoY calculations
    prev_year_data = None
    
    for data in sorted_data:
        # Get values, handling None values
        total_revenue = float(getattr(data, 'total_revenue', 0) or 0)
        revenue_yoy_change = getattr(data, 'revenue_yoy_change', None)
        gross_profit = float(getattr(data, 'gross_profit', 0) or 0)
        gross_profit_margin = getattr(data, 'gross_profit_margin', None)
        gross_profit_yoy_change = getattr(data, 'gross_profit_yoy_change', None)
        operating_profit = float(getattr(data, 'operating_profit', 0) or 0)
        operating_profit_margin = getattr(data, 'operating_profit_margin', None)
        operating_profit_yoy_change = getattr(data, 'operating_profit_yoy_change', None)
        net_profit = float(getattr(data, 'net_profit', 0) or getattr(data, 'net_profit', 0) or 0)
        net_profit_margin = getattr(data, 'net_profit_margin', None) or getattr(data, 'net_profit_margin', None)
        net_profit_yoy_change = getattr(data, 'net_profit_yoy_change', None) or getattr(data, 'net_profit_yoy_change', None)
        number_of_shares = float(getattr(data, 'number_of_shares', 0) or 0)
        free_cash_flow = float(getattr(data, 'free_cash_flow', 0) or 0)
        free_cash_flow_yoy_change = getattr(data, 'free_cash_flow_yoy_change', None)
        eps = getattr(data, 'eps', None)
        price_high = getattr(data, 'price_high', None) or getattr(data, 'eps_high', None)
        price_low = getattr(data, 'price_low', None) or getattr(data, 'eps_low', None)
        earning_power = getattr(data, 'earning_power', None)
        dividends_per_share = getattr(data, 'dividends_per_share', None)
        dividend_rate = getattr(data, 'dividend_rate', None)
        
        # Get asset account values
        return_on_equity = getattr(data, 'return_on_equity', None)
        return_on_assets = getattr(data, 'return_on_assets', None)
        return_on_invested_capital = getattr(data, 'return_on_invested_capital', None)
        book_value = getattr(data, 'book_value', None)
        book_value_per_share = getattr(data, 'book_value_per_share', None)
        book_value_yoy_change = getattr(data, 'book_value_yoy_change', None)
        current_ratio = getattr(data, 'current_ratio', None)
        
        # Calculate margins if not provided
        if gross_profit_margin is None and total_revenue:
            gross_profit_margin = gross_profit / total_revenue
            
        if operating_profit_margin is None and total_revenue:
            operating_profit_margin = operating_profit / total_revenue
            
        if net_profit_margin is None and total_revenue:
            net_profit_margin = net_profit / total_revenue
            
        # Calculate ratios if not provided
        if return_on_equity is None and net_profit and getattr(data, 'shareholders_equity', 0):
            shareholders_equity = float(getattr(data, 'shareholders_equity', 0) or 0)
            return_on_equity = net_profit / shareholders_equity if shareholders_equity else 0
            
        if return_on_assets is None and net_profit and getattr(data, 'total_assets', 0):
            total_assets = float(getattr(data, 'total_assets', 0) or 0)
            return_on_assets = net_profit / total_assets if total_assets else 0
            
        # if current_ratio is None and getattr(data, 'current_assets', 0) and getattr(data, 'current_liabilities', 0):
        #     current_assets = float(getattr(data, 'current_assets', 0) or 0)
        #     current_liabilities = float(getattr(data, 'current_liabilities', 0) or 0)
        #     current_ratio = current_assets / current_liabilities if current_liabilities else 0
            
        if book_value_per_share is None and getattr(data, 'shareholders_equity', 0) and number_of_shares:
            shareholders_equity = float(getattr(data, 'shareholders_equity', 0) or 0)
            book_value_per_share = shareholders_equity / number_of_shares if number_of_shares else 0
        
        # Initialize YoY dictionary
        yoy = {
            "revenue": revenue_yoy_change,
            "gross_profit": gross_profit_yoy_change,
            "operating_profit": operating_profit_yoy_change,
            "net_profit": net_profit_yoy_change,
            "free_cash_flow": free_cash_flow_yoy_change,
            "book_value": book_value_yoy_change,
            "roa": None,
            "roe": None
        }
        
        # Calculate YoY changes if previous year data exists and not already provided
        if prev_year_data:
            # Helper function to calculate percentage change
            def calc_percent_change(current, previous):
                if previous and previous != 0:
                    return round((current - previous) / abs(previous) * 100, 2)
                return None
            
            # Only calculate YoY changes if not already provided
            if revenue_yoy_change is None:
                prev_total_revenue = float(getattr(prev_year_data, 'total_revenue', 0) or 0)
                yoy["revenue"] = calc_percent_change(total_revenue, prev_total_revenue)
                
            if gross_profit_yoy_change is None:
                prev_gross_profit = float(getattr(prev_year_data, 'gross_profit', 0) or 0)
                yoy["gross_profit"] = calc_percent_change(gross_profit, prev_gross_profit)
                
            if operating_profit_yoy_change is None:
                prev_operating_profit = float(getattr(prev_year_data, 'operating_profit', 0) or 0)
                yoy["operating_profit"] = calc_percent_change(operating_profit, prev_operating_profit)
                
            if net_profit_yoy_change is None:
                prev_net_profit = float(getattr(prev_year_data, 'net_profit', 0) or getattr(prev_year_data, 'net_profit', 0) or 0)
                yoy["net_profit"] = calc_percent_change(net_profit, prev_net_profit)
                
            if free_cash_flow_yoy_change is None:
                prev_free_cash_flow = float(getattr(prev_year_data, 'free_cash_flow', 0) or 0)
                yoy["free_cash_flow"] = calc_percent_change(free_cash_flow, prev_free_cash_flow)
                
            if book_value_yoy_change is None and book_value is not None:
                prev_book_value = getattr(prev_year_data, 'book_value', None)
                if prev_book_value:
                    yoy["book_value"] = calc_percent_change(book_value, prev_book_value)
            
            # YoY for calculated ratios
            if return_on_assets is not None:
                prev_return_on_assets = getattr(prev_year_data, 'return_on_assets', None)
                if prev_return_on_assets:
                    yoy["roa"] = calc_percent_change(return_on_assets, prev_return_on_assets)
                    
            if return_on_equity is not None:
                prev_return_on_equity = getattr(prev_year_data, 'return_on_equity', None)
                if prev_return_on_equity:
                    yoy["roe"] = calc_percent_change(return_on_equity, prev_return_on_equity)
        
        # Create metric object
        metric = {
            "year": data.fiscal_year,
            "revenue": total_revenue,
            "revenue_yoy_change": revenue_yoy_change,
            "gross_profit": gross_profit,
            "gross_profit_margin": gross_profit_margin,
            "gross_profit_yoy_change": gross_profit_yoy_change,
            "operating_profit": operating_profit,
            "operating_profit_margin": operating_profit_margin,
            "operating_profit_yoy_change": operating_profit_yoy_change,
            "net_profit": net_profit,
            "net_profit_margin": net_profit_margin,
            "net_profit_yoy_change": net_profit_yoy_change,
            "free_cash_flow": free_cash_flow,
            "free_cash_flow_yoy_change": free_cash_flow_yoy_change,
            "number_of_shares": number_of_shares,
            
            # Asset account ratios
            "return_on_equity": return_on_equity,
            "return_on_assets": return_on_assets,
            "return_on_invested_capital": return_on_invested_capital,
            "book_value": book_value,
            "book_value_per_share": book_value_per_share,
            "book_value_yoy_change": book_value_yoy_change,
            "current_ratio": current_ratio,
            "eps": eps,
            "price_high": price_high,
            "price_low": price_low,
            "earning_power": earning_power,
            "dividends_per_share": dividends_per_share,
            "dividend_rate": dividend_rate,
            
            # YoY changes
            "yoy": yoy
        }
        
        metrics.append(metric)
        prev_year_data = data
    
    return {
        "company": company_name,
        "metrics": metrics
    }


# Create router
router = APIRouter(
    prefix="/financial",
    tags=["financial"],
    responses={404: {"description": "Not found"}},
)


# API Endpoints
@router.post("/companies/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    print("current_user", current_user)
    """Create a new company"""
    try:
        db_company = Company(name=company.name, created_by=current_user.get("id"))
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this name already exists"
        )


@router.get("/companies/", response_model=List[CompanyResponse])
def get_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all companies"""
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies


@router.get("/companies/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific company by ID"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/companies/{company_id}/financial-data/", response_model=FinancialDataResponse)
def create_financial_data(
    company_id: int,
    financial_data: FinancialDataCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create financial data for a specific company and fiscal year"""
    # Check if company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    try:
        # Calculate margins
        gross_profit_margin = None
        operating_profit_margin = None
        net_profit_margin = None
        
        if financial_data.total_revenue > 0:
            gross_profit_margin = financial_data.gross_profit / financial_data.total_revenue
            operating_profit_margin = financial_data.operating_profit / financial_data.total_revenue
            net_profit_margin = financial_data.net_profit / financial_data.total_revenue
            
        # Get previous year's data for YoY calculations
        previous_year = str(int(financial_data.fiscal_year) - 1)
        previous_data = db.query(FinancialData).filter(
            FinancialData.company_id == company_id,
            FinancialData.fiscal_year == previous_year
        ).first()
        
        # Initialize YoY fields
        revenue_yoy_change = None
        gross_profit_yoy_change = None
        operating_profit_yoy_change = None
        net_profit_yoy_change = None
        free_cash_flow_yoy_change = None
        book_value_yoy_change = None
        
        # Calculate YoY changes if previous year data exists
        if previous_data:
            # Helper function to calculate percentage change
            def calc_percent_change(current, previous):
                if previous and previous != 0:
                    return round((current - previous) / abs(previous) * 100, 2)
                return None
            
            revenue_yoy_change = calc_percent_change(
                financial_data.total_revenue, previous_data.total_revenue)
            
            gross_profit_yoy_change = calc_percent_change(
                financial_data.gross_profit, previous_data.gross_profit)
            
            operating_profit_yoy_change = calc_percent_change(
                financial_data.operating_profit, previous_data.operating_profit)
            
            net_profit_yoy_change = calc_percent_change(
                financial_data.net_profit, previous_data.net_profit)
            
            free_cash_flow_yoy_change = calc_percent_change(
                financial_data.free_cash_flow, previous_data.free_cash_flow)
            
            if financial_data.book_value is not None and previous_data.book_value is not None:
                book_value_yoy_change = calc_percent_change(
                    financial_data.book_value, previous_data.book_value)
        
        # Check if financial data for this company and fiscal year already exists
        existing_data = db.query(FinancialData).filter(
            FinancialData.company_id == company_id,
            FinancialData.fiscal_year == financial_data.fiscal_year
        ).first()
        
        if existing_data:
            # Update existing record with base fields
            for key, value in financial_data.dict().items():
                setattr(existing_data, key, value)
            
            # Update calculated fields
            existing_data.gross_profit_margin = gross_profit_margin
            existing_data.operating_profit_margin = operating_profit_margin
            existing_data.net_profit_margin = net_profit_margin
            existing_data.revenue_yoy_change = revenue_yoy_change
            existing_data.gross_profit_yoy_change = gross_profit_yoy_change
            existing_data.operating_profit_yoy_change = operating_profit_yoy_change
            existing_data.net_profit_yoy_change = net_profit_yoy_change
            existing_data.free_cash_flow_yoy_change = free_cash_flow_yoy_change
            existing_data.book_value_yoy_change = book_value_yoy_change
            
            db_financial_data = existing_data
        else:
            # Create new financial data entry
            db_financial_data = FinancialData(
                company_id=company_id,
                fiscal_year=financial_data.fiscal_year,
                prepared_by=financial_data.prepared_by,
                notes=financial_data.notes,
                
                # Income Accounts Analysis
                total_revenue=financial_data.total_revenue,
                gross_profit=financial_data.gross_profit,
                operating_profit=financial_data.operating_profit,
                net_profit=financial_data.net_profit,
                number_of_shares=financial_data.number_of_shares,
                eps=financial_data.eps,
                price_high=financial_data.price_high,
                price_low=financial_data.price_low,
                earning_power=financial_data.earning_power,
                free_cash_flow=financial_data.free_cash_flow,
                
                # Calculated margins
                gross_profit_margin=gross_profit_margin,
                operating_profit_margin=operating_profit_margin,
                net_profit_margin=net_profit_margin,
                
                # Calculated YoY changes
                revenue_yoy_change=revenue_yoy_change,
                gross_profit_yoy_change=gross_profit_yoy_change,
                operating_profit_yoy_change=operating_profit_yoy_change,
                net_profit_yoy_change=net_profit_yoy_change,
                free_cash_flow_yoy_change=free_cash_flow_yoy_change,
                
                # Assets Accounts Analysis
                return_on_equity=financial_data.return_on_equity,
                return_on_assets=financial_data.return_on_assets,
                return_on_invested_capital=financial_data.return_on_invested_capital,
                book_value=financial_data.book_value,
                book_value_per_share=financial_data.book_value_per_share,
                book_value_yoy_change=book_value_yoy_change,
                current_ratio=financial_data.current_ratio,
                
                # Dividends Accounts Analysis
                dividends_per_share=financial_data.dividends_per_share,
                dividend_rate=financial_data.dividend_rate
            )
            db.add(db_financial_data)
        
        db.commit()
        db.refresh(db_financial_data)
        return db_financial_data
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error saving financial data: {str(e)}"
        )


@router.get("/companies/{company_id}/financial-data/", response_model=List[FinancialDataResponse])
def get_financial_data_by_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all financial data for a specific company"""
    # Check if company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    financial_data = db.query(FinancialData).filter(FinancialData.company_id == company_id).all()
    return financial_data


@router.get("/companies/{company_id}/financial-data/{fiscal_year}", response_model=FinancialDataResponse)
def get_financial_data_by_year(
    company_id: int,
    fiscal_year: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get financial data for a specific company and fiscal year"""
    financial_data = db.query(FinancialData).filter(
        FinancialData.company_id == company_id,
        FinancialData.fiscal_year == fiscal_year
    ).first()
    
    if financial_data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Financial data for company ID {company_id} and fiscal year {fiscal_year} not found"
        )
    
    return financial_data


@router.put("/companies/{company_id}/financial-data/{fiscal_year}", response_model=FinancialDataResponse)
def update_financial_data(
    company_id: int,
    fiscal_year: str,
    financial_data: FinancialDataCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update financial data for a specific company and fiscal year"""
    # Check if financial data exists
    db_financial_data = db.query(FinancialData).filter(
        FinancialData.company_id == company_id,
        FinancialData.fiscal_year == fiscal_year
    ).first()
    
    if db_financial_data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Financial data for company ID {company_id} and fiscal year {fiscal_year} not found"
        )
    
    # Calculate margins
    gross_profit_margin = None
    operating_profit_margin = None
    net_profit_margin = None
    
    if financial_data.total_revenue > 0:
        gross_profit_margin = financial_data.gross_profit / financial_data.total_revenue
        operating_profit_margin = financial_data.operating_profit / financial_data.total_revenue
        net_profit_margin = financial_data.net_profit / financial_data.total_revenue
        
    # Get previous year's data for YoY calculations
    previous_year = str(int(fiscal_year) - 1)
    previous_data = db.query(FinancialData).filter(
        FinancialData.company_id == company_id,
        FinancialData.fiscal_year == previous_year
    ).first()
    
    # Initialize YoY fields
    revenue_yoy_change = None
    gross_profit_yoy_change = None
    operating_profit_yoy_change = None
    net_profit_yoy_change = None
    free_cash_flow_yoy_change = None
    book_value_yoy_change = None
    
    # Calculate YoY changes if previous year data exists
    if previous_data:
        # Helper function to calculate percentage change
        def calc_percent_change(current, previous):
            if previous and previous != 0:
                return round((current - previous) / abs(previous) * 100, 2)
            return None
        
        revenue_yoy_change = calc_percent_change(
            financial_data.total_revenue, previous_data.total_revenue)
        
        gross_profit_yoy_change = calc_percent_change(
            financial_data.gross_profit, previous_data.gross_profit)
        
        operating_profit_yoy_change = calc_percent_change(
            financial_data.operating_profit, previous_data.operating_profit)
        
        net_profit_yoy_change = calc_percent_change(
            financial_data.net_profit, previous_data.net_profit)
        
        free_cash_flow_yoy_change = calc_percent_change(
            financial_data.free_cash_flow, previous_data.free_cash_flow)
        
        if financial_data.book_value is not None and previous_data.book_value is not None:
            book_value_yoy_change = calc_percent_change(
                financial_data.book_value, previous_data.book_value)
    
    # Update base fields from input
    for key, value in financial_data.dict().items():
        if key != "fiscal_year":  # Don't update the fiscal year as it's part of the primary key
            setattr(db_financial_data, key, value)
    
    # Update calculated fields
    db_financial_data.gross_profit_margin = gross_profit_margin
    db_financial_data.operating_profit_margin = operating_profit_margin
    db_financial_data.net_profit_margin = net_profit_margin
    db_financial_data.revenue_yoy_change = revenue_yoy_change
    db_financial_data.gross_profit_yoy_change = gross_profit_yoy_change
    db_financial_data.operating_profit_yoy_change = operating_profit_yoy_change
    db_financial_data.net_profit_yoy_change = net_profit_yoy_change
    db_financial_data.free_cash_flow_yoy_change = free_cash_flow_yoy_change
    db_financial_data.book_value_yoy_change = book_value_yoy_change
    
    db.commit()
    db.refresh(db_financial_data)
    return db_financial_data


@router.delete("/companies/{company_id}/financial-data/{fiscal_year}", status_code=status.HTTP_204_NO_CONTENT)
def delete_financial_data(
    company_id: int,
    fiscal_year: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete financial data for a specific company and fiscal year"""
    # Check if financial data exists
    db_financial_data = db.query(FinancialData).filter(
        FinancialData.company_id == company_id,
        FinancialData.fiscal_year == fiscal_year
    ).first()
    
    if db_financial_data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Financial data for company ID {company_id} and fiscal year {fiscal_year} not found"
        )
    
    db.delete(db_financial_data)
    db.commit()
    return None 


@router.get("/companies/{company_id}/dashboard", response_model=DashboardResponse)
def get_dashboard_data(
    company_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get processed financial data for dashboard display"""
    # Check if company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get all financial data for the company
    financial_data = db.query(FinancialData).filter(FinancialData.company_id == company_id).all()
    
    # Calculate metrics
    dashboard_data = calculate_financial_metrics(financial_data, str(company.name))
    
    return dashboard_data 