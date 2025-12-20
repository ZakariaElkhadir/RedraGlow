import hid

VENDOR_ID = 0x258a
PRODUCT_ID = 0x0049


def main():
    for device in hid.enumerate(VENDOR_ID, PRODUCT_ID):
        for k, v in device.items():
            print(f"{k}: {v}")
        print("\n" + "-" * 40 + "\n")


if __name__ == "__main__":
    main()
