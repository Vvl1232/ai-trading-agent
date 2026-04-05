import logging
import pandas as pd
from sec_api import InsiderTradingApi
from utils.config import SEC_API_KEY, SEC_QUERY_RANGE

logger = logging.getLogger(__name__)

api = InsiderTradingApi(api_key=SEC_API_KEY)


def get_sec_data():
    """
    Fetch insider trading data from SEC API.
    
    Returns:
        dict: Raw insider trading data
        
    Raises:
        Exception: If API call fails
    """
    try:
        logger.info(f"Fetching SEC insider trading data for range: {SEC_QUERY_RANGE}")
        
        data = api.get_data({
            "query": f"transactionDate:[{SEC_QUERY_RANGE} TO NOW]",
            "sortBy": "transactionDate"
        })
        
        if not data:
            logger.warning("No SEC data returned from API")
            return {}
        
        logger.info(f"Successfully fetched {len(data.get('data', []))} insider trades")
        return data
        
    except Exception as e:
        logger.error(f"Failed to fetch SEC data: {str(e)}")
        raise


def get_top5_trades(data):
    """
    Extract top 5 most recent insider trades by transaction value.
    
    Args:
        data (dict): Raw SEC insider trading data
        
    Returns:
        pd.DataFrame: Top 5 trades with columns: issuerTradingSymbol, 
                     transactionDate, transactionType, shares, price
                     
    Raises:
        ValueError: If data format is invalid
    """
    try:
        if not data or "data" not in data:
            logger.warning("Invalid data format for top5 extraction")
            return pd.DataFrame()
        
        trades_list = data.get("data", [])
        
        if not trades_list:
            logger.warning("No trades found in SEC data")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(trades_list)
        
        # Validate required columns
        required_cols = ["issuerTradingSymbol"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing columns in SEC data: {missing_cols}")
            return pd.DataFrame()
        
        # Sort by transaction date (most recent first)
        if "transactionDate" in df.columns:
            df["transactionDate"] = pd.to_datetime(df["transactionDate"], errors="coerce")
            df = df.sort_values("transactionDate", ascending=False)
        
        # Get top 5
        top5 = df.head(5)
        logger.info(f"Top 5 trades: {top5['issuerTradingSymbol'].tolist()}")
        
        return top5
        
    except Exception as e:
        logger.error(f"Failed to extract top 5 trades: {str(e)}")
        raise ValueError(f"Error processing SEC data: {str(e)}")