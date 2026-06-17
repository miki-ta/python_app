# モデルのダウンロード --- (*1)
! wget https://huggingface.co/mmnga/ELYZA-japanese-Llama-2-7b-instruct-gguf/resolve/main/ELYZA-japanese-Llama-2-7b-instruct-q4_K_M.gguf
# ダウンロードしたモデルのパスを指定
MODEL_PATH = "./ELYZA-japanese-Llama-2-7b-instruct-q4_K_M.gguf"

from llama_cpp import Llama
def generate_text(prompt):
 # Llamaのオブジェクトを作成
 llm = Llama(model_path=MODEL_PATH)
 # プロンプトテンプレートに合わせて入力テキストを整形 --- (*2)
 sys = "あなたは誠実で優秀な日本人のアシスタントです。"
 prompt_in = f"[INST] <<SYS>>{sys}<</SYS>>{prompt} [/INST]"
 response = llm(prompt_in, max_tokens=256)
 # 結果を返す
 return response["choices"][0]["text"]

# テキストを生成して表示
print(generate_text("信号機の色を3色答えてください。"))
