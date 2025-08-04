from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, UniqueConstraint, Text
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    financial_data = relationship("FinancialData", back_populates="company", cascade="all, delete-orphan")
    user = relationship("Users")


class FinancialData(Base):
    __tablename__ = 'financial_data'

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    fiscal_year = Column(String, nullable=False)
    prepared_by = Column(String)
    notes = Column(Text)
    
    # Income Accounts Analysis
    total_revenue = Column(Float, nullable=False)
    revenue_yoy_change = Column(Float, nullable=True)
    gross_profit = Column(Float, nullable=False)
    gross_profit_margin = Column(Float, nullable=True)
    gross_profit_yoy_change = Column(Float, nullable=True)
    operating_profit = Column(Float, nullable=False)
    operating_profit_margin = Column(Float, nullable=True)
    operating_profit_yoy_change = Column(Float, nullable=True)
    net_profit = Column(Float, nullable=False)
    net_profit_margin = Column(Float, nullable=True)
    net_profit_yoy_change = Column(Float, nullable=True)
    number_of_shares = Column(Float, nullable=False)
    price_high = Column(Float, nullable=False)
    price_low = Column(Float, nullable=False)
    eps = Column(Float, nullable=False, default=0)
    earning_power = Column(Float, nullable=True)
    free_cash_flow = Column(Float, nullable=False)
    free_cash_flow_yoy_change = Column(Float, nullable=True)
    
    # Assets Accounts Analysis
    return_on_equity = Column(Float, nullable=True)
    return_on_assets = Column(Float, nullable=True)
    return_on_invested_capital = Column(Float, nullable=True)
    book_value = Column(Float, nullable=True)
    book_value_per_share = Column(Float, nullable=True)
    book_value_yoy_change = Column(Float, nullable=True)
    current_ratio = Column(Float, nullable=True)
    
    # Legacy fields - keeping for backward compatibility
    total_assets = Column(Float, nullable=True)
    total_liabilities = Column(Float, nullable=True)
    shareholders_equity = Column(Float, nullable=True)
    current_assets = Column(Float, nullable=True)
    current_liabilities = Column(Float, nullable=True)
    
    # Dividends Accounts Analysis
    dividends_per_share = Column(Float, nullable=False)
    dividend_rate = Column(Float, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="financial_data")
    
    # Ensure each company can only have one record per fiscal year
    __table_args__ = (
        UniqueConstraint('company_id', 'fiscal_year', name='uix_company_fiscal_year'),
    )
