"""体重・身長・体脂肪率からBMI判定とワンポイントアドバイスを表示するデスクトップアプリ。"""

import tkinter as tk
from tkinter import messagebox, ttk


# 文字列で入力された値を「数値(float)」として安全に扱うための共通関数。
# 例: "65.5" -> 65.5
def validate_float(value_text, label_name, minimum=None, maximum=None):
    """入力文字列を数値に変換し、必要に応じて範囲チェックを行う。"""
    try:
        # float()で数値に変換。数値でない場合はValueErrorになる。
        value = float(value_text)
    except ValueError as error:
        raise ValueError(f"{label_name}は数値で入力してください。") from error

    # 入力可能な最小値・最大値が指定されている場合は範囲チェックする。
    if minimum is not None and value < minimum:
        raise ValueError(f"{label_name}は{minimum}以上の値を入力してください。")
    if maximum is not None and value > maximum:
        raise ValueError(f"{label_name}は{maximum}以下の値を入力してください。")

    return value


# BMIの計算式: 体重(kg) ÷ 身長(m)^2
def calculate_bmi(weight_kg, height_cm):
    """体重と身長からBMIを計算する。"""
    # 身長はcm入力なので、まずmに変換する。
    height_m = height_cm / 100
    return weight_kg / (height_m * height_m)


# BMIと体脂肪率の組み合わせで、判定名とアドバイス文を返す。
# 戻り値は (判定文字列, アドバイス文字列) のタプル。
def get_result_and_advice(bmi, body_fat):
    """BMIと体脂肪率から判定結果と総合アドバイスを返す。"""
    # BMI 18.5未満: やせ型
    if bmi < 18.5:
        return (
            "やせ型",
            "栄養バランスの良い食事と軽い筋トレで、少しずつ健康的に体重を増やしましょう。",
        )

    # BMI 18.5以上25未満: 標準型
    if bmi < 25:
        # 標準BMIでも体脂肪率が高い場合は、体組成改善寄りの助言にする。
        if body_fat >= 25:
            return (
                "標準型",
                "体脂肪率が高めです。筋トレを増やして、食事は脂質と糖質を少し意識して整えましょう。",
            )
        return (
            "標準型",
            "今の状態を保つことが大切です。運動とバランスの良い食事を続けましょう。",
        )

    # BMI 25以上30未満: 肥満（軽）型
    if bmi < 30:
        # 体脂肪率も高い場合は脂肪減少を強めに提案。
        if body_fat >= 30:
            return (
                "肥満（軽）型",
                "有酸素運動と食事管理を組み合わせて、体脂肪を少しずつ減らしましょう。",
            )
        return (
            "肥満（軽）型",
            "食べすぎを見直し、毎日の歩行や軽い運動を増やしていきましょう。",
        )

    # BMI 30以上: 肥満（重）型
    # さらに体脂肪率が高い場合は、専門家相談も含む文言にする。
    if body_fat >= 35:
        return (
            "肥満（重）型",
            "体脂肪率も高めです。無理のない範囲で、医師や栄養士に相談しながら改善を進めましょう。",
        )
    return (
        "肥満（重）型",
        "まずは生活習慣の見直しから始めましょう。食事と運動を少しずつ整えるのがポイントです。",
    )


# BMI値だけに注目した、シンプルなワンポイント助言を返す。
def get_bmi_advice(bmi):
    """BMI値に応じたワンポイントアドバイスを返す。"""
    if bmi < 18.5:
        return "BMIが低めです。1日3食を基本に、たんぱく質と炭水化物をしっかり取りましょう。"
    if bmi < 25:
        return "BMIは標準範囲です。現在の生活習慣を維持しつつ、週2〜3回の運動を続けましょう。"
    if bmi < 30:
        return "BMIがやや高めです。間食や夜食を控え、毎日20〜30分の有酸素運動を意識しましょう。"
    return "BMIが高い状態です。急な減量は避け、食事記録と軽い運動から段階的に改善しましょう。"


# 「判定する」ボタンを押したときに呼ばれるメイン処理。
def on_calculate():
    """入力値を読み取り、判定結果とアドバイスを表示する。"""
    try:
        # 入力欄の文字列を読み込み、数値変換 + 妥当範囲チェックを行う。
        weight = validate_float(weight_var.get(), "体重(kg)", minimum=20, maximum=300)
        height = validate_float(height_var.get(), "身長(cm)", minimum=50, maximum=250)
        body_fat = validate_float(body_fat_var.get(), "体脂肪率(%)", minimum=0, maximum=70)
    except ValueError as error:
        # ユーザー入力に問題がある場合は、ステータスとダイアログで通知する。
        status_text.set(f"入力エラー: {error}")
        messagebox.showerror("入力エラー", str(error))
        return

    try:
        # BMI計算と、2種類の助言文を作成する。
        bmi = calculate_bmi(weight, height)
        result, advice = get_result_and_advice(bmi, body_fat)
        bmi_advice = get_bmi_advice(bmi)
    except Exception as error:  # noqa: BLE001
        # 想定外の例外をまとめて表示し、処理を中断する。
        status_text.set(f"処理エラー: {error}")
        messagebox.showerror("処理エラー", f"予期しないエラーが発生しました。\n{error}")
        return

    # 「結果」エリア上部に、判定名とBMI実測値を表示する。
    bmi_result_text.set(
        f"BMI判定: {result}\n"
        f"BMI測定値: {bmi:.1f}"
    )

    # 「総合アドバイス」エリアに、2種類の助言をまとめて表示する。
    advice_result_text.set(
        f"BMI値に応じたアドバイス:\n{bmi_advice}\n\n"
        f"BMIと体脂肪率に応じたアドバイス:\n{advice}"
    )
    status_text.set("判定が完了しました。")


def on_clear():
    """入力欄と結果表示をリセットする。"""
    # 入力欄・結果欄・ステータス欄を初期状態に戻す。
    weight_var.set("")
    height_var.set("")
    body_fat_var.set("")
    bmi_result_text.set("")
    advice_result_text.set("入力後に「判定する」を押してください。")
    status_text.set("入力をクリアしました。")


# Tkinterのメインウィンドウを作成。
root = tk.Tk()
root.title("BMI・体脂肪率 判定アプリ")

# 画面サイズに応じて初期ウィンドウサイズを決める。
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = min(640, max(520, screen_width - 80))
window_height = min(760, max(620, screen_height - 80))
root.geometry(f"{window_width}x{window_height}")

# ユーザーが縮めすぎて表示が崩れないよう、最小サイズを設定する。
root.minsize(520, 620)
root.resizable(True, True)

# 見た目(フォントやテーマ)の設定。
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Yu Gothic UI", 11))
style.configure("TButton", font=("Yu Gothic UI", 11, "bold"))
style.configure("Title.TLabel", font=("Yu Gothic UI", 18, "bold"))
style.configure("Result.TLabel", font=("Yu Gothic UI", 14, "bold"))

# 画面全体のコンテナ。
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

# タイトルと説明文。
ttk.Label(main_frame, text="BMI・体脂肪率 判定アプリ", style="Title.TLabel").pack(anchor="w")
description_label = ttk.Label(
    main_frame,
    text="体重・身長・体脂肪率を入力すると、BMI判定結果と体脂肪率を考慮したアドバイスを表示します。",
    wraplength=560,
    justify="left",
)
description_label.pack(anchor="w", pady=(6, 16))

# 入力欄のまとまり。
input_frame = ttk.LabelFrame(main_frame, text="入力", padding=14)
input_frame.pack(fill="x")

# 画面の表示内容を保持する変数。
weight_var = tk.StringVar()
height_var = tk.StringVar()
body_fat_var = tk.StringVar()
bmi_result_text = tk.StringVar(value="")
advice_result_text = tk.StringVar(value="入力後に「判定する」を押してください。")
status_text = tk.StringVar(value="値を入力して「判定する」を押してください。")

# 体重・身長・体脂肪率の入力欄を配置。
ttk.Label(input_frame, text="体重(kg)").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
weight_entry = ttk.Entry(input_frame, textvariable=weight_var, width=20)
weight_entry.grid(row=0, column=1, sticky="w", pady=6)

ttk.Label(input_frame, text="身長(cm)").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
height_entry = ttk.Entry(input_frame, textvariable=height_var, width=20)
height_entry.grid(row=1, column=1, sticky="w", pady=6)

ttk.Label(input_frame, text="体脂肪率(%)").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=6)
body_fat_entry = ttk.Entry(input_frame, textvariable=body_fat_var, width=20)
body_fat_entry.grid(row=2, column=1, sticky="w", pady=6)

# ボタンとステータスメッセージの行。
button_frame = ttk.Frame(main_frame)
button_frame.pack(fill="x", pady=(14, 10))

ttk.Button(button_frame, text="判定する", command=on_calculate).pack(side="left")
ttk.Button(button_frame, text="クリア", command=on_clear).pack(side="left", padx=10)
ttk.Label(button_frame, textvariable=status_text).pack(side="left", padx=(14, 0))

# 結果表示エリア。
output_frame = ttk.LabelFrame(main_frame, text="結果", padding=14)
output_frame.pack(fill="both", expand=True)

# 上段: BMI判定結果。
bmi_result_label = ttk.Label(
    output_frame,
    textvariable=bmi_result_text,
    style="Result.TLabel",
    justify="left",
    wraplength=540,
)
bmi_result_label.pack(anchor="w", pady=(4, 12))

ttk.Separator(output_frame).pack(fill="x", pady=(0, 12))

# 下段: アドバイス表示。
ttk.Label(output_frame, text="総合アドバイス", font=("Yu Gothic UI", 11, "bold")).pack(anchor="w")
advice_result_label = ttk.Label(output_frame, textvariable=advice_result_text, wraplength=540, justify="left")
advice_result_label.pack(anchor="w", pady=(4, 0))


# ウィンドウ幅が変わったときに折り返し幅を再計算する。
def update_wraplength(_event):
    """ウィンドウ幅に応じて折り返し位置を更新し、表示切れを防ぐ。"""
    wrap = max(main_frame.winfo_width() - 60, 320)
    description_label.configure(wraplength=wrap)
    bmi_result_label.configure(wraplength=wrap)
    advice_result_label.configure(wraplength=wrap)


# 起動直後に体重入力へカーソルを当てる。
weight_entry.focus()

# 画面リサイズ時の折り返し更新イベントを登録。
root.bind("<Configure>", update_wraplength)

# Enterキーで判定処理を実行できるようにする。
root.bind("<Return>", lambda _event: on_calculate())

# Tkinterのイベントループを開始。
root.mainloop()