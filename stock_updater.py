import os
from datetime import datetime
import time
import yfinance as yf
from notion_client import Client
from dotenv import load_dotenv
import pytz

load_dotenv()

# Notion API 配置
notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("DATABASE_ID")

def get_stock_price(symbol):
    """获取股票最新价格和涨幅"""
    try:
        stock = yf.Ticker(symbol)
        price = stock.info.get('regularMarketPrice')
        # 获取涨幅（当日涨幅百分比）
        change_percent = stock.info.get('regularMarketChangePercent')
        # 将涨幅百分比转换为小数并保留两位小数
        if change_percent is not None:
            change_percent = round(change_percent/100, 4)
        
        if price is None:
            print(f"无法获取 {symbol} 的价格数据")
        return price, change_percent
    except Exception as e:
        print(f"获取股票价格出错: {e}")
        return None, None

def update_stock_price(page):
    """更新单个股票价格和涨幅"""
    try:
        # 获取公司信息
        company = page["properties"]["Name"]["title"][0]["plain_text"]
        stock_symbol = page["properties"]["股票代码"]["rich_text"][0]["text"]["content"]
        
        print(f"\n处理: {company}({stock_symbol})")
        
        # 获取并更新股价和涨幅
        price, change_percent = get_stock_price(stock_symbol)
        
        if price is not None:
            notion.pages.update(
                page_id=page["id"],
                properties={
                    "最新股价": {"number": price},
                    "今日涨": {"number": change_percent},  # 更新涨幅字段
                    "更新时间": {"date": {"start": datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()}}
                }
            )
            print(f"已更新股价: {price}，涨幅: {change_percent}%")
            return True
    except Exception as e:
        print(f"更新失败: {e}")
    return False

def update_notion_stock_prices():
    """更新所有股票价格"""
    try:
        pages = notion.databases.query(database_id=DATABASE_ID).get("results")
        print(f"开始更新 {len(pages)} 条记录...")
        
        success_count = 0
        for page in pages:
            if update_stock_price(page):
                success_count += 1
            time.sleep(1)  # 避免请求过于频繁
            
        print(f"\n更新完成: 成功 {success_count}/{len(pages)}")
    except Exception as e:
        print(f"更新过程出错: {e}")

def main():
    print(f"\n开始更新股票价格... {datetime.now()}")
    update_notion_stock_prices()

if __name__ == "__main__":
    main() 