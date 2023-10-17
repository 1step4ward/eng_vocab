import pandas as pd
import datetime
import engword as ew

wl = ew.WordList('test.json')

print(wl.get_num_total_words())
# print(wl.delete_word('new1'))
# print(wl.delete_word('new2'))
# print(wl.delete_word('new3'))
# print(wl.delete_word('new4'))
# print(wl.delete_word('new5'))
# print(wl.df)
# print(wl.add_word('new1'))
# print(wl.add_word('new2'))
# print(wl.add_word('new3'))
# print(wl.add_word('new4'))
# print(wl.add_word('new5'))
# wl.update_word('new1', True)
print(wl.add_word('composability'))
# print(wl.delete_word('predictable'))
print(wl.get_target_words())
print(wl.df)
wl.save_json()
