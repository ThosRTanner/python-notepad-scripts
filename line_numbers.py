from Npp import editor, STYLESCOMMON

def main():
    editor.setMarginWidthN(0, editor.textWidth(STYLESCOMMON.LINENUMBER, "_99999"))

if __name__ == "__main__":
    main()
