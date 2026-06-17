from llama_cpp import Llama

# ダウンロードしたモデルファイルのパスを指定 --- (*1)
MODEL_PATH = "./vicuna-7b-cot.Q4_K_M.gguf"

# テキストを生成する関数 --- (*2)
def generate_text(prompt):
  # Llamaのオブジェクトを作成 --- (*3)
  llm = Llama(model_path=MODEL_PATH)
  # Vicuna用のプロンプトテンプレートに合わせて入力テキストを整形 --- (*4)
  response = llm(f"User:{prompt}\nAssistant:", max_tokens=1000)
  # 結果を返す
  return response["choices"][0]["text"]

# テキストを生成して表示 --- (*5)
print(generate_text("信号機の色を3色答えてください。"))
