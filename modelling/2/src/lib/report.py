from typing import List

class ReportFiller:
    @staticmethod
    def clean_absorbing_states(matrix: List[List[str]], zero_str: str = '$0$') -> List[List[str]]:
        n = len(matrix)
        if n == 0:
            return []

        absorbing = [
            i for i in range(n)
            if all(cell == zero_str for cell in matrix[i])
        ]

        if not absorbing:
            return [row[:] for row in matrix]

        absorbing_set = set(absorbing)

        cleaned = [
            [cell for j, cell in enumerate(matrix[i]) if j not in absorbing_set]
            for i in range(n)
            if i not in absorbing_set
        ]

        header = [''] + [str(i) for i in range(n) if i not in absorbing_set]
        result = [header]
        for row_idx, row in zip(
            (i for i in range(n) if i not in absorbing_set),
            cleaned,
        ):
            result.append([str(row_idx)] + row)

        return result