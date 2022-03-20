python3.9 -m cProfile -o profile.prof chess_ai/chess_test.py
python3.9 -m flameprof profile.prof > profile.svg