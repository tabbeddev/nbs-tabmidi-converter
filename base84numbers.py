NUMBERS_LOOKUP = "0123456789abcdefghijklmnopqrstuvwxyzâĉêĝĥîĵôŝûŵŷẑáćéǵíjḱĺḿńóṕŕ!§%&/()=?{[]}+*-,.;:_#"


def convert_84(input: int) -> str:
    a = input % 84
    b = input // 84

    if b:
        return convert_84(b) + NUMBERS_LOOKUP[a]
    return NUMBERS_LOOKUP[a]


# Just for me to understand to logic
def convert_10(input: str) -> int:
    value = 0

    for index, letter in enumerate(input):
        plain_number = NUMBERS_LOOKUP.find(letter)
        matters = 84 ** (len(input) - index - 1)

        value += plain_number * matters

    return value
