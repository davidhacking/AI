import xxoo, alpha_beta_ai, ai


def test_ai_first_start():
    xo = xxoo.XXOO()
    mmAI = alpha_beta_ai.AlphaBetaAI()
    next_pace = mmAI.next_pace(xo)
    print(next_pace, next_pace.pace == 5)


def test_play_must_win():
    xo = xxoo.XXOO(paces={
        1: ai.player_type_player, 2: ai.player_type_player, 3: None,
        4: ai.player_type_ai, 5: ai.player_type_ai, 6: None,
        7: None, 8: None, 9: None,
    })
    mmAI = alpha_beta_ai.AlphaBetaAI()
    next_pace = mmAI.next_pace(xo)
    print(next_pace, next_pace.pace == 3)


def test_play_cut_ai():
    ox = xxoo.XXOO(paces={
        1: ai.player_type_player, 2: ai.player_type_ai, 3: ai.player_type_player,
        4: ai.player_type_ai, 5: ai.player_type_ai, 6: None,
        7: ai.player_type_ai, 8: ai.player_type_player, 9: None,
    })
    mmAI = alpha_beta_ai.AlphaBetaAI()
    next_pace = mmAI.next_pace(ox)
    print(next_pace, next_pace.pace == 6)


def test_play_cut_ai2():
    xo = xxoo.XXOO(paces={
        1: ai.player_type_player, 2: None, 3: None,
        4: ai.player_type_ai, 5: ai.player_type_ai, 6: None,
        7: None, 8: ai.player_type_player, 9: None,
    })
    mmAI = alpha_beta_ai.AlphaBetaAI()
    next_pace = mmAI.next_pace(xo)
    print(next_pace, next_pace.pace == 6)


def test_player_win():
    xo = xxoo.XXOO(paces={
        1: ai.player_type_ai, 2: ai.player_type_ai, 3: ai.player_type_player,
        4: ai.player_type_ai, 5: ai.player_type_player, 6: None,
        7: None, 8: None, 9: None,
    })
    mmAI = alpha_beta_ai.AlphaBetaAI()
    next_pace = mmAI.next_pace(xo)
    print(next_pace, next_pace.pace == 7)


def init():
    xxoo.init_point_map()


init()


def test_interact():
    print('-----------')
    print(' 1 | 2 | 3')
    print('-----------')
    print(' 4 | 5 | 6')
    print('-----------')
    print(' 7 | 8 | 9')
    print('-----------')
    print('你是"X"玩家，输入1~9的数字：')
    xo = xxoo.XXOO(paces={
        1: None, 2: None, 3: None,
        4: None, 5: None, 6: None,
        7: None, 8: None, 9: None,
    })
    while not xo.end():
        pace = int(input().strip()[0])
        xo.play(pace, ai.player_type_ai)
        mmAI = alpha_beta_ai.AlphaBetaAI()
        choice = mmAI.next_pace(xo)
        if choice is None:
            xo.draw_broad()
            break
        print("ai choice={}".format(choice))
        xo.play(choice.pace, ai.player_type_player)
        xo.draw_broad()
    print("the end")


if __name__ == '__main__':
    test_play_cut_ai()
    test_play_cut_ai2()
    test_ai_first_start()
    test_play_must_win()
    test_player_win()
    test_interact()
