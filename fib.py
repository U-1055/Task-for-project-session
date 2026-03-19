
# Python 3.12.3

def gen_fib(start_: int, end_: int) -> list[int]:
    last_nums = [0, 1]
    sequence = []
    while last_nums[1] <= end_:
        second = last_nums[1]
        last_nums[1] = last_nums[0] + last_nums[1]
        if last_nums[0] >= start_:
            sequence.append(last_nums[0])
        last_nums[0] = second

    sequence.append(last_nums[0])

    return sequence


NO_NUMS = 'В заданном диапазоне нет чисел Фибоначчи'
start, end = map(int, input().split())

if start < end:
    res = gen_fib(start, end)
    print(' '.join(map(str, res)) if res else NO_NUMS)
else:
    print(NO_NUMS)
