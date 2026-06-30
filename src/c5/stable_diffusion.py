import torch
from diffusers import StableDiffusionPipeline
from IPython.display import display_png

# 描画に利用するモデルを指定する --- (*1)
MODEL = "CompVis/stable-diffusion-v1-4"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Stable Diffusionを利用して画像の生成を行う関数 --- (*2)
def generate_image(prompt, save_path, seed=99999):
    # パイプラインの初期化 --- (*3)
    pipeline = StableDiffusionPipeline.from_pretrained(MODEL).to(DEVICE)
    # 描画に利用する乱数シードを指定 --- (*4)
    generator = torch.Generator().manual_seed(seed)
    # パイプラインで画像を生成 --- (*5)
    with torch.autocast(DEVICE):
        image = pipeline(prompt, guidance_scale=7.5, generator=generator).images[0]
        # 画像を保存 --- (*6)
        image.save(save_path)
    return image

# 生成する画像のプロンプトを指定して画像を生成 --- (*7)
prompt = "(masterpiece), Giraff in the forest, water paint"
image = generate_image(prompt, "sd_image.png")
# 画像を表示する --- (*8)
display_png(image)
