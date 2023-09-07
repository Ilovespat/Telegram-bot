import unittest
import datetime
from collections import OrderedDict

REPLACE_VALUES = OrderedDict(
    [(".", ""), (",", ""), ("/", ""), ("-", ""), (" ", ""), ("января", "01"), ("февраля", "02"),
     ("марта", "03"), ("апреля", "04"), ("мая", "05"), ("июня", "06"), ("июля", "07"), ("августа", "08"),
     ("сентября", "09"), ("октября", "10"), ("ноября", "11"), ("декабря", "12"), ])


# Замена введенных символов даты рождения на дату в формате ДД.ММ.ГГ
def multiple_replace(source_str):
    for i, j in REPLACE_VALUES.items():
        source_str = source_str.replace(i, j)
    return source_str


# Расчет суммы цифр для вычисления "Числа судьбы"
def numerolog(message):
    list_num = []
    try:
        mess = message.lower()
        num = multiple_replace(mess)
        if len(num) != 8:
            numdate = datetime.datetime.strptime(num, '%d%m%y').date().strftime('%d%m%Y')
        else:
            numdate = num
        list_num.extend(str(numdate))
        res = sum(map(int, numdate))
        while res >= 10:
            list_num.clear()
            for i in str(res):
                list_num.append(int(i))
            res = sum(list_num)
        return res
    except Exception:
        res = 'Ой, это не дата или что-то пошло не так.'
        return res


class TestAddition(unittest.TestCase):

    def test_numerolog_sum(self):
        self.assertEqual(numerolog("250493"), 6)

    def test_numerolog_word(self):
        self.assertEqual(numerolog("25 fghtkz 93"), 'Ой, это не дата или что-то пошло не так.')

    def test_multiple_replace_sign(self):
        self.assertEqual(multiple_replace("25,04,93-"), "250493")

    def test_multiple_replace_word(self):
        self.assertEqual(multiple_replace("25 апреля 1993"), "25041993")


if __name__ == '__main__':
    unittest.main()

