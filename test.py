import tkinter as tk
import datetime as dt


def Tester(x,y):
	print(x + y)



with open(r"tester.txt", "w")as F:
	t = str(dt.datetime.today())
	F.write(t)

