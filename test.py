if __name__ == "__main__":
    text = "$HK199.00"
    text_length = len(text)
    if ".00" and "$" in text and "HK" not in text and text_length < 13:
    # if ".00" and "$" in text and text_length < 13:
        # if "HK" not in text:
        print("Good")
    else:
        print("BAD")