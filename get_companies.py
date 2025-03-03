import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

# Notion API 配置
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

def get_company_names():
    """获取数据库中所有公司名称"""
    try:
        # 获取数据库中所有页面
        pages = notion.databases.query(
            database_id=DATABASE_ID
        ).get("results")
        
        # 提取所有公司名称
        companies = []
        for page in pages:
            try:
                company = page["properties"].get("Name", {}).get("title", [])[0]["plain_text"]
                companies.append(company)
            except (IndexError, KeyError) as e:
                print(f"处理某条记录时出错: {e}")
                continue
        
        # 用逗号连接所有公司名称
        result = ",".join(companies)
        print(result)
        return result
        
    except Exception as e:
        print(f"获取公司名称时出错: {e}")
        return ""

if __name__ == "__main__":
    get_company_names() 