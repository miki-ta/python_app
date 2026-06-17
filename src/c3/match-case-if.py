for no in range(10, 21):
    match no:
        case i if no % 3 == 0 and no % 5 == 0:
            print(f"{no}は…3の倍数かつ5の倍数")
        case i if no % 3 == 0:
            print(f"{no}は…3の倍数")
        case i if no % 5 == 0:
            print(f"{no}は…5の倍数")
