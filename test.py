import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def new_fetch_and_visualize_financial_data(keywords: list, timeframe: int, companies: list):
    companies_all = ["amat", "amd", "asml", "avgo", "intc", "lrcx", "mu", "nvda", "qcom", "ssnlf", "tsm", "txn"]
    companies = [company for company in companies if company in companies_all]
    current_year = 2023  # Current year as mentioned
    start_year = current_year - timeframe + 1
    df_dict = {}
    for keyword in keywords:
        df_list = []
        for company in companies:
            # Load excel file into datafram
            try:
                df = pd.read_excel(f'./xlsxs/{company}_financial_statement.xlsx')
            except FileNotFoundError as E:
                print(E)
            # df = pd.read_excel(file)
            df['Year'] = df['Year'].round().astype('Int64')
            # Filter rows for timeframe and keyword
            df = df[df['Year'].between(start_year, current_year)]
            df = df[['Year', keyword]]
            # Add company name to the dataframe
            df['Company'] = company
            df_list.append(df)
        # Concatenate all dataframes
        final_df = pd.concat(df_list)
        # Store this DataFrame in a dict with the keyword as key
        df_dict[keyword] = final_df
        # Plotting
        plt.figure(figsize=(10, 6))
        for company in companies:
            subset = final_df[final_df['Company'] == company]
            plt.plot(subset['Year'], subset[keyword], label=company)
        plt.title(f'{keyword} over Last {timeframe} Years')
        plt.xlabel('Year')
        plt.ylabel(keyword)
        plt.legend()
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.show()

functions = [
    {
        "name": "fetch_and_visualize_financial_data",
        "description": "Fetch and visualize financial data trends",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items":{
                        "type":"string"
                    },
                    "description": "Financial keyword pick relevant from ['Year', 'Revenue', 'Cost of Revenue', 'Gross Profit', 'Operating Expenses', 'Selling, General and Administrative Expenses', 'General and Administrative Expenses', 'Research and Development Expenses', 'Other Expenses', 'Cost and Expenses', 'Operating Income', 'Interest Expense', 'Income Tax Expense', 'Earnings before Tax', 'Net Income', 'Earnings Per Share Basic', 'Earnings Per Share Diluted', 'Weighted Average Shares Outstanding', 'Weighted Average Shares Outstanding (Diluted)', 'Gross Margin', 'EBIT Margin', 'Profit Margin', 'EBITDA', 'Earnings Before Tax Margin', 'Retained Earnings (Previous Year)', 'Net Income.1', 'Stock Dividends', 'Dividend Paid', 'Retained Earnings', 'Gross PPE', 'Annual Depreciation', 'Capital Expenditure', 'Net PPE']"
                },
                "timeframe": {
                    "type": "number",
                    "description": "Timeframe for the data trend, e.g., 'last 5 years' would mean timeframe is 5",
                },
                "company": {
                    "type": "array",
                    "items":{
                        "type":"string",
                        "enum":["amat", "amd", "asml", "avgo", "intc", "lrcx", "mu", "nvda", "qcom", "ssnlf", "tsm", "txn"]
                    },
                    "description": "List of Company Tokens",
                },
            }
        }
    }
]

if __name__ == '__main__':
    while True:
        query = input("Input your query: ")

        response = openai.ChatCompletion.create(temperature=0,
                                     model="gpt-3.5-turbo-0613",
                                     messages=[{"role": "user", "content": query}],
                                     functions=functions,
                                     function_call="auto")
        response_message = response["choices"][0]["message"]

        if response_message.get("function_call"):
            keywords = response_message["function_call"]["arguments"].get("keywords")
            timeframe = response_message["function_call"]["arguments"].get("timeframe")
            company = response_message["function_call"]["arguments"].get("company")

            new_fetch_and_visualize_financial_data(keywords=keywords, timeframe=timeframe, companies=company)