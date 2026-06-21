"""BMIと体脂肪率から判定とワンポイントアドバイスを出すデスクトップアプリ。"""  

import tkinter as tk
from tkinter import messagebox, ttk


def validate_float(value_text, label_name, minimum=None, maximum=None):
    """入力文字列を数値に変換し、必要なら範囲チェックも行う。"""
    try:
        value = float(value_text)
    except ValueError as error:
        raise ValueError(f"{label_name}は数値で入力してください。") from error

    if minimum is not None and value < minimum:
        raise ValueError(f"{label_name}は{minimum}以上の値を入力してください。")
    if maximum is not None and value > maximum:
        raise ValueError(f"{label_name}は{maximum}以下の値を入力してください。")

    return value


def calculate_bmi(weight_kg, height_cm):
    """体重と身長からBMIを計算する。"""
    height_m = height_cm / 100
    return weight_kg / (height_m * height_m)


def get_result_and_advice(bmi, body_fat):
    """BMIと体脂肪率から判定結果とアドバイスを決める。"""
    if bmi < 18.5:
        return (
            "やせ型",
            "栄養バランスの良い食事と軽い筋トレで、少しずつ健康的に体重を増やしましょう。",
        )
    if bmi < 25:
        if body_fat >= 25:
            return (
                "標準型",
                "体脂肪率が高めです。筋トレを増やして、食事は脂質と糖質を少し意識して整えましょう。",
            )
        return (
            "標準型",
            "今の状態を保つことが大切です。運動とバランスの良い食事を続けましょう。",
        )
    if bmi < 30:
        if body_fat >= 30:
            return (
                "肥満（軽）型",
                "有酸素運動と食事管理を組み合わせて、体脂肪を少しずつ減らしましょう。",
            )
        return (
            "肥満（軽）型",
            "食べすぎを見直し、毎日の歩行や軽い運動を増やしていきましょう。",
        )

    if body_fat >= 35:
        return (
            "肥満（重）型",
            "体脂肪率も高めです。無理のない範囲で、医師や栄養士に相談しながら改善を進めましょう。",
        )
    return (
        "肥満（重）型",
        "まずは生活習慣の見直しから始めましょう。食事と運動を少しずつ整えるのがポイントです。",
    )


def get_bmi_advice(bmi):
    """BMI値に応じたアドバイスを返す。"""
    if bmi < 18.5:
        return "BMIが低めです。1日3食を基本に、たんぱく質と炭水化物をしっかり取りましょう。"
    if bmi < 25:
        return "BMIは標準範囲です。現在の生活習慣を維持しつつ、週2〜3回の運動を続けましょう。"
    if bmi < 30:
        return "BMIがやや高めです。間食や夜食を控え、毎日20〜30分の有酸素運動を意識しましょう。"
    return "BMIが高い状態です。急な減量は避け、食事記録と軽い運動から段階的に改善しましょう。"


def on_calculate():
    """ボタンが押されたときに入力値を読み取り、結果を画面に表示する。"""
    try:
        weight = validate_float(weight_var.get(), "体重(kg)", minimum=20, maximum=300)
        height = validate_float(height_var.get(), "身長(cm)", minimum=50, maximum=250)
        body_fat = validate_float(body_fat_var.get(), "体脂肪率(%)", minimum=0, maximum=70)
    except ValueError as error:
        status_text.set(f"入力エラー: {error}")
        messagebox.showerror("入力エラー", str(error))
        return

    try:
        bmi = calculate_bmi(weight, height)
        result, advice = get_result_and_advice(bmi, body_fat)
        bmi_advice = get_bmi_advice(bmi)
    except Exception as error:  # noqa: BLE001
        status_text.set(f"処理エラー: {error}")
        messagebox.showerror("処理エラー", f"予期しないエラーが発生しました。\n{error}")
        return

    bmi_result_text.set(
        f"判定結果: {result}\n"
        f"BMI値: {bmi:.1f}\n"
        f"体脂肪率: {body_fat:.1f}%"
    )
    advice_result_text.set(f"アドバイス: {bmi_advice}\n\n補足: {advice}")
    status_text.set("判定が完了しました。")


def on_clear():
    """入力欄と結果表示をリセットする。"""
    weight_var.set("")
    height_var.set("")
    body_fat_var.set("")
    bmi_result_text.set("判定結果: -\nBMI値: -\n体脂肪率: -")
    advice_result_text.set("入力後に「判定する」を押してください。")
    status_text.set("入力をクリアしました。")


root = tk.Tk()
root.title("BMI・体脂肪率 判定アプリ")
root.geometry("560x420")
root.resizable(False, False)

# 画面全体の見た目を少し整えて、入力しやすい配置にします。
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Yu Gothic UI", 11))
style.configure("TButton", font=("Yu Gothic UI", 11, "bold"))
style.configure("Title.TLabel", font=("Yu Gothic UI", 18, "bold"))
style.configure("Result.TLabel", font=("Yu Gothic UI", 14, "bold"))

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

ttk.Label(main_frame, text="BMI・体脂肪率 判定アプリ", style="Title.TLabel").pack(anchor="w")
ttk.Label(
    main_frame,
    text="体重・身長・体脂肪率を入力して、結果とワンポイントアドバイスを確認します。",
).pack(anchor="w", pady=(6, 16))

input_frame = ttk.LabelFrame(main_frame, text="入力", padding=14)
input_frame.pack(fill="x")

weight_var = tk.StringVar()
height_var = tk.StringVar()
body_fat_var = tk.StringVar()
bmi_result_text = tk.StringVar(value="判定結果: -\nBMI値: -\n体脂肪率: -")
advice_result_text = tk.StringVar(value="入力後に「判定する」を押してください。")
status_text = tk.StringVar(value="値を入力して「判定する」を押してください。")

ttk.Label(input_frame, text="体重(kg)").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
weight_entry = ttk.Entry(input_frame, textvariable=weight_var, width=20)
weight_entry.grid(row=0, column=1, sticky="w", pady=6)

ttk.Label(input_frame, text="身長(cm)").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
height_entry = ttk.Entry(input_frame, textvariable=height_var, width=20)
height_entry.grid(row=1, column=1, sticky="w", pady=6)

ttk.Label(input_frame, text="体脂肪率(%)").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=6)
body_fat_entry = ttk.Entry(input_frame, textvariable=body_fat_var, width=20)
body_fat_entry.grid(row=2, column=1, sticky="w", pady=6)

button_frame = ttk.Frame(main_frame)
button_frame.pack(fill="x", pady=(14, 10))

ttk.Button(button_frame, text="判定する", command=on_calculate).pack(side="left")
ttk.Button(button_frame, text="クリア", command=on_clear).pack(side="left", padx=10)
ttk.Label(button_frame, textvariable=status_text).pack(side="left", padx=(14, 0))

output_frame = ttk.LabelFrame(main_frame, text="結果", padding=14)
output_frame.pack(fill="both", expand=True)

ttk.Label(output_frame, text="判定結果", font=("Yu Gothic UI", 11, "bold")).pack(anchor="w")
ttk.Label(output_frame, textvariable=bmi_result_text, style="Result.TLabel", justify="left", wraplength=500).pack(anchor="w", pady=(4, 12))

ttk.Separator(output_frame).pack(fill="x", pady=(0, 12))

ttk.Label(output_frame, text="アドバイス", font=("Yu Gothic UI", 11, "bold")).pack(anchor="w")
ttk.Label(output_frame, textvariable=advice_result_text, wraplength=500, justify="left").pack(anchor="w", pady=(4, 0))

# 起動した直後から入力しやすいように、体重欄にフォーカスを置きます。
weight_entry.focus()

root.bind("<Return>", lambda _event: on_calculate())

# アプリを起動します。
root.mainloop()