#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertoolsю
# Можно свободно определять свои функции и т.п.
# -----------------

import itertools

def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, [max(ranks)], [])
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks, [])
    elif straight(ranks):
        return (4, [max(ranks)], [])
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks, [])


def real_value(rank):
    """Возвращает реальную ценность карты (для сравнения)"""
    cr = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    rn = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    for ls in zip(cr, rn):
        if rank == ls[0]:
            return ls[1]


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    list = [x[0] for x in hand if x[0] != '?']
    list = sorted([real_value(x) for x in list], reverse=True)
    return list


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    list = [x[1] for x in hand]
    list = set(list)
    return len(list) == 1


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    for i in range(0, len(ranks) - 4):
        rv = [x for x in ranks[i:i+5]]
        value_range = max(rv) - min(rv)
        if (value_range == 4 and len(set(rv)) == 5):
            return True
    return False


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    for r in ranks:
        if ranks.count(r) == n:
            return [r]


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    counts = {}
    for r in ranks:
        if r not in counts:
            counts[r] = 0
        counts[r] += 1
    vals = [key for key in counts.keys() if counts[key]==2]
    return vals


def check_comb(cb, best):
    """Проверка лучшей комбинации"""
    val = hand_rank(cb)

    avg_1 = 0
    if val[1]:
        avg_1 = sum(val[1]) / len(val[1])

    avg_2 = 0
    if val[2]:
        avg_2 = sum(val[2]) / len(val[2])

    case_1 = (val[0] > best['val'][0])
    case_2 = (val[0] == best['val'][0] and avg_1 > best['val'][1])
    case_3 = (val[0] == best['val'][0] and avg_1 == best['val'][1] and avg_2 > best['val'][2])

    if (case_1 or case_2 or case_3):
        best['val'] = [val[0], avg_1, avg_2]
        best['comb'] = sorted(cb)

    return best


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    best = {'comb': '', 'val': [0, 0, 0]}

    for cb in itertools.combinations(hand, 5):
        best = check_comb(cb, best)

    return best['comb']


def best_wild_hand(hand):
    """best_hand но с джокерами"""

    best = {'comb': '', 'val': [0, 0, 0]}

    # Варианты замены джокера для данной руки
    jokers = get_jokers(hand)

    hand_wrap = [hand]

    # Замена джокеров на все варианты, создание списка комбинаций
    hand_wrap = replace_jokers(hand_wrap, jokers)

    # Убираем все варианты с повторами и меньше 7 карт
    hand_final = []
    for item in hand_wrap:
        item = set(item)
        if len(item) == 7:
            hand_final.append(item)

    # Проверка всех групп по 5 карт
    for hand_jk in hand_final:
        for cb in itertools.combinations(hand_jk, 5):
            best = check_comb(cb, best)


    return best['comb']


def get_jokers(hand):
    """Функция генерит все варианты замены джокеров"""

    list_rank = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    jk = {'?R' : ['D', 'H'], '?B' : ['C', 'S']}
    jokers = {}

    for key in jk.keys():
        if (key in hand):
            add = []
            for item in itertools.product(*[list_rank, jk[key]]):
                add.append(item[0] + item[1])
            jokers[key] = add

    return jokers


def replace_jokers(hand_wrap, jokers):
    """'Рука' размножается на множество 'рук' с каждым вариантом замены джокера """

    for key in jokers.keys():
        hand_new = []
        for hand_elem in hand_wrap:
            if key in hand_elem:
                hand_elem.remove(key)
                for joker in jokers[key]:
                    hand_new.append(hand_elem + [joker])
        if len(hand_new) > 0:
            hand_wrap = hand_new

    return hand_wrap


def test_best_hand():
    print "test_best_hand..."
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'


def test_best_wild_hand():
    print "test_best_wild_hand..."
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'

if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()
