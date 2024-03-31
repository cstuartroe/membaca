def levenshtein_diffs(s1, s2, sub_penalty=1.5):
    diffs = [[(0, 0, 0)]]

    for j in range(1, len(s2)+1):
        diffs[-1].append((0, -1, j))

    for i in range(1, len(s1)+1):
        diffs.append([(-1, 0, i)])

        for j in range(1, len(s2)+1):
            x, y, d = 0, -1, diffs[i][j - 1][2] + 1
            if diffs[i - 1][j][2] + 1 < d:
                x, y, d = -1, 0, diffs[i - 1][j][2] + 1

            sub_cost = 0 if s1[i-1] == s2[j-1] else sub_penalty
            if diffs[i - 1][j - 1][2] + sub_cost < d:
                x, y, d = -1, -1, diffs[i-1][j-1][2] + sub_cost

            diffs[-1].append((x, y, d))

    return diffs


def levenshtein(s1, s2, sub_penalty=1.5):
    diffs = levenshtein_diffs(s1, s2, sub_penalty)
    return diffs[-1][-1][-1]