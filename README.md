# Merge CSV

A simple [Kivy](http://kivy.org) application for merging CSV files.

This is not a particularly "clean" or well-structured application.  I share it in case it may be useful or inspire some idea.

## Basic Usage

```
python main.py CSV_INPUT_ONE CSV_INPUT_TWO . . . CSV_INPUT_N
```

To remove a field from the output, double-click on the field in the output column.

To add or redirect a field in the input, either double-click on the input field twice, or double-click once, enter the name your want the field to have in the output, and press enter. 

## Screenshot

![screenshot](docs/screenshot.png)

## Saving and Loading Mappings

This feature allows you to save all of your actions, and re-apply them to similar files.

If you check "record" in the bottom-left of the screen, all of the field removing/renaming/adding will be recorded.  You can save this recording to a text file by entering a path into the text field between the "save" and "load" buttons.  To load and apply a mappings file, enter a path and click "load."

**NOTE**: saving will not warn you if you are going to overwrite a file.

## Misc.

**NOTE**: when saving the merged output, the output is written to a temporary file and then copied to the path you specify.  Thus, if you are saving over a file and something goes wrong, the file you're overwriting won't be corrupted.