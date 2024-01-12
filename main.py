import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import openai



class App():
    def __init__(self):
        # Playwrightを初期化
        vimium_path = os.path.abspath("./vimium-master")

        self.context = (
            sync_playwright()
            .start()
            .chromium.launch_persistent_context(
                "",
                headless=True,
                args=[
                    f"--disable-extensions-except={vimium_path}",
                    f"--load-extension={vimium_path}",
                ],
                ignore_https_errors=True,
            )
        )

        self.page = self.context.new_page()
        self.page.set_viewport_size({"width": 1080, "height": 720})

        # プロンプト読み込み
        with open("./prompts/get_action.txt", "r") as f:
            self.prompt_get_action = f.read()

    # OpenAI GPT
    def run_gpt(self, prompt=""):
        # GPTの関数を定義する
        functions = [
            {
                "name": "select_element",
                "description": "xPathを指定して要素を選択し、選択の説明を提供します。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "選択する要素のxPath",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "この要素を選択した理由",
                        },
                    },
                    "required": ["id", "explanation"],
                },
            }
        ]
        res = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            functions=functions,
            function_call={"name": "select_element"},
            max_tokens=300,
        )

        return res

    # HTML整形：scriptとstyleを除去する
    def filter_html(self, html_string):
        soup = BeautifulSoup(html_string, "html.parser")

        for script in soup(["script", "style"]):
            script.decompose()

        # テキストに変換
        text = str(soup)
        return text

    # HTMLを取得する
    def get_html(self):
        # このページの整形後のHTMLを取得する
        filtered_html = self.filter_html(self.page.content())
        return filtered_html

    # ページ遷移
    def navigate(self, url):
        
        self.page.goto(url=url if "://" in url else "http://" + url, timeout=0)

    # テスト実行
    def run_ui_test(self):
        # テストシナリオを読み込む
        with open("test.feature", "r") as f:
            test_feature = f.read()

        # ページのHTMLを取得する
        html = self.get_html()


if __name__ == '__main__':
    url = ""
    # 初期化
    app = App()

    # ページ遷移
    app.navigate(url)


    # テスト実行
    app.run_ui_test(url)