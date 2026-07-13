import flet as ft
import requests

API_URL = "http://127.0.0.1:8000"

def main(page: ft.Page):
    page.title = "AI Stock Analyzer"

    stock_input = ft.TextField(label="Stock Symbol")
    result = ft.Text()

    def analyze(e):
        try:
            symbol = stock_input.value

            response = requests.get(
                f"{API_URL}/stock/{symbol}"
            )

            result.value = str(response.json())

        except Exception as ex:
            result.value = f"Error: {ex}"

        page.update()

    page.add(
        stock_input,
        ft.ElevatedButton(
            "Analyze Stock",
            on_click=analyze
        ),
        result
    )

ft.app(target=main)