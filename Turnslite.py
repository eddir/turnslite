import asyncio
import logging
import sys

from aiogram import types

from utils import switch

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] <%(filename)s:%(lineno)d> %(message)s'))
logger.addHandler(handler)

# Входные значения
CSE = "Сотрудник входит"
CSQ = "Сотрудник выходит"
CF = "Приложили недействительную карту"
GV = "Охранник открыл турникет на вход и выход"
GE = "Охранник открыл турникет на вход"
GQ = "Охранник открыл турникет на выход"
GX = "Охранник закрыл турникет"
GR = "Охранник запращивает список сотрудников в здании"
N = "Карта действительна"

# Возвращаемые значения
X = "Турникет закрыт, красный крест"
E = "Турникет открыт на вход"
Q = "Турникет открыт на выход"
B = "Приложенная карта неверная"
CE = "Турникет открыт на вход, сотрудник записан"
CQ = "Турникнт открыт на выход, сотрудник исключен"
V = "Турникет открыт на вход и выход"
R = "Возвращает список всех сотрудников в здании"

# Состояния автомата
SO = "Турникет открыт"
SC = "Турникет закрыт"
SOD = "Турникет открыт на N секунд"
SNE = "Проверка карты для входа"
SNQ = "Проверка карты для выхода"

# Задержка перед закрытием
DELAY = 5


class Turnslite:

    def __init__(self, bot):
        self.bot = bot
        self.recipient = None
        self.state = SC

        self.states_map = {
            SC: [CF, GX, GE, GQ, GR, CSE, CSQ, GV],
            SO: [GV, GR, GX],
            SNE: [],
            SNQ: [],
            SOD: [CSE, CSQ],
        }

        self.employers = [
            [1, "Сотрудник 1"],
            [15, "Сотрудник 2"],
            [21, "Сотрудник 3"],
            [35, "Сотрудник 4"],
        ]
        self.visitors = [1]

        logger.debug("Turnslite has been created")
        logger.debug("State: %s" % self.state)

    def send(self, message):
        logger.debug([text for text in self.states_map[self.state]])

        if len(self.states_map[self.state]) > 0:
            keyboard_markup = types.ReplyKeyboardMarkup(row_width=2)
            keyboard_markup.add(*(types.KeyboardButton(text) for text in self.states_map[self.state]))
        else:
            keyboard_markup = types.ReplyKeyboardRemove()

        asyncio.create_task(
            self.bot.send_message(self.recipient, message, reply_markup=keyboard_markup)
        )

    def output(self, signal):
        logger.info(signal)
        if signal is R:
            logger.info("Output: %s", self.visitors)
            self.send("Сейчас в здании:\n" + "\n".join(
                [("#%d - %s" % (employee[0], employee[1])) for employee in self.employers if
                 employee[0] in self.visitors]
            ))
            returnt

        self.send(signal)
        logger.info("Output: %s", signal)
        logger.debug("State: %s" % self.state)

    def input(self):
        return input()

    def valid(self, card_number):
        for employee in self.employers:
            if employee[0] == card_number:
                return True
        return False

    def visit(self, employee):
        self.visitors.append(employee)

    def leave(self, employee):
        self.visitors.remove(employee)

    def pending_close(self, recipient):
        asyncio.create_task(
            self.delay(self.cycle, recipient, CSE)
        )

    async def delay(self, callback, *args):
        await asyncio.sleep(DELAY)
        callback(*args)

    def cycle(self, recipient, input):
        self.recipient = recipient
        capture = input
        for case in switch(self.state):
            if case(SC):
                if capture in (CF, GX):
                    self.output(X)
                elif capture in GE:
                    self.output(E)
                elif capture in GQ:
                    self.output(Q)
                elif capture in GR:
                    self.output(R)
                elif capture in CSE:
                    self.state = SNE
                    self.output(X)
                elif capture in CSQ:
                    self.state = SNQ
                    self.output(X)
                elif capture in GV:
                    self.state = SO
                    self.output(V)
                break
            if case(SNE):
                card_number = int(capture) if capture.isdigit() else None
                if self.valid(card_number):
                    self.state = SOD
                    self.visit(card_number)
                    self.output(E)
                    self.pending_close(recipient)
                else:
                    self.state = SC
                    self.output(B)
                break
            if case(SOD):
                if capture in (CSQ, CSE):
                    self.state = SC
                    self.output(X)
                break
            if case(SNQ):
                card_number = int(capture)
                if self.valid(card_number):
                    self.leave(card_number)
                    self.state = SOD
                    self.output(Q)
                else:
                    self.state = SC
                    self.output(B)
                break
            if case(SO):
                if capture in GV:
                    self.output(V)
                elif capture in GR:
                    self.output(R)
                elif capture in GX:
                    self.state = SC
                    self.output(X)
                break

            raise Exception("Unknown state")
