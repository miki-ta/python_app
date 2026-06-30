for no in range(10, 21):
    match (no % 3 == 0, no % 5 == 0):
        case (True, False):
            print(f"{no}は…3の倍数")
        case (False, True):
            print(f"{no}は…5の倍数")
        case (True, True):
            print(f"{no}は…3の倍数かつ5の倍数")
