from tkinter import PhotoImage


def applyBasic(root, GUIManager):
    uniformColor = "#ffffff"
    root.title("Unifix Groupon Scraper")
    photo = PhotoImage(file="Coloring/logo.png")
    root.iconphoto(True, photo)
    root.config(bg=uniformColor)

    for widget in GUIManager.widgets:
        widget.configure(bg=uniformColor)
    return root



