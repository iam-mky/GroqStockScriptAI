
import yfinance as yf

def get_stock_data(ticker_symbol:str):
    """
    Fetches market metrics and trend data for a given ticker symbol.
    
    Returns a dict with stock metrics, or None if the retrieval fails.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        
        # Pull asset information metrics
        info = stock.info
        
        # Pull 6 month daily historical trend data
        history = stock.history(period="6mo")
        
        # Extract recent trend data structure if available
        recent_history = []
        if not history.empty:
            history_reset = history.reset_index()
            history_reset['Date'] = history_reset['Date'].dt.strftime('%Y-%m-%d')
            recent_history = history_reset[['Date', 'Close', 'Volume']].to_dict(orient='records')
            
            # Use fallback values from recent history if .info fields are missing
            current_price = info.get('currentPrice') or float(history['Close'].iloc[-1])
            current_volume = info.get('volume') or int(history['Volume'].iloc[-1])
        else:
            current_price = info.get('currentPrice')
            current_volume = info.get('volume')

        return {
            "ticker": ticker_symbol,
            "price": current_price,
            "volume": current_volume,
            "pe_ratio": info.get('trailingPE'),
            "recent_history": recent_history
        }
        
    except Exception as e:
        # Graceful failure return per "don't over-validate, just catch failures" design
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return None


