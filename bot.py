import random
import logging
logging.basicConfig(filename="info.log", filemode='w', level=logging.DEBUG)

#https://peaceful-atoll-58092.herokuapp.com/

class Robot:
    def __init__(self, _size=10):
        logging.info("Bot created")
        self.size = _size
        self.mode = 'easy'
        self.ships = []
        self.rest_ships = []
        self.enemy_ships = []
        self.win_enemy = False
        self.win_me = False
        self.is_injure = False
        self.my_moves = []
        self.direction_of_last_injure = 0  # h - горизонтально, v - вертикально
        self.current_enemy_ship = []
        self.previous_command = ''
        self.my_previous_step = (-1, -1)
        self.table = []
        self.enemy_rest_cells = []
        self.enemy_table = []
        self.enemy_ships_size = []

    def start(self):
        logging.info("Start the game")
        self.generate_table()
        self.enemy_table = [[0] * self.size for i in range(self.size)]
        self.enemy_rest_cells = [(i, j) for i in range(0, self.size) for j in range(0, self.size)]
        self.enemy_ships_size = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

    def generate_table(self):
        logging.info("Creating table")
        my_table = [[0] * self.size for i in range(self.size)]
        free_cells = [(i, j) for i in range(0, self.size) for j in range(0, self.size)]

        # ставим корабли
        self.generate_ship(free_cells, my_table, 4)
        self.generate_ship(free_cells, my_table, 3)
        self.generate_ship(free_cells, my_table, 3)
        self.generate_ship(free_cells, my_table, 2)
        self.generate_ship(free_cells, my_table, 2)
        self.generate_ship(free_cells, my_table, 2)
        self.generate_ship(free_cells, my_table, 1)
        self.generate_ship(free_cells, my_table, 1)
        self.generate_ship(free_cells, my_table, 1)
        self.generate_ship(free_cells, my_table, 1)

        self.table = my_table

    def generate_ship(self, free_cells, my_table, size_ship):
        logging.info("Generation ship of size" + str(size_ship))
        # будем рассматривать только 2 направления от выбранной клетки - вниз и вправо
        ship_put = False
        while not ship_put:

            curr_cell = random.choice(free_cells)
            correct_directions = []
            if curr_cell[0] + size_ship <= self.size:
                correct_directions.append((1, 0))

            if curr_cell[1] + size_ship <= self.size:
                correct_directions.append((0, 1))

            if len(correct_directions) > 0:
                direction = random.choice(correct_directions)

                # проверяем, что в выбранном направлении можем поставить корабль
                i = 1
                success = True
                while i < size_ship and success:
                    if free_cells.count((curr_cell[0] + i * direction[0], curr_cell[1] + i * direction[1])) == 0:
                        success = False
                    i += 1

                if success:
                    ship_put = True

        current_ship = []
        for k in range(size_ship):
            current_ship.append((curr_cell[0], curr_cell[1]))
            my_table[curr_cell[0]][curr_cell[1]] = 2
            self.delete_used_cells(free_cells, curr_cell)
            curr_cell = (curr_cell[0] + direction[0], curr_cell[1] + direction[1])

        self.ships.append(current_ship)
        self.rest_ships.append(current_ship)

    def delete_used_cells(self, free_cells, curr_cell):
        all_directions = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (1, 1), (-1, -1), (-1, 1)]
        for direction in all_directions:
            cell = (curr_cell[0] + direction[0], curr_cell[1] + direction[1])
            if free_cells.count(cell) > 0:
                free_cells.remove(cell)

    def print_rest_ships(self):
        result = ''
        for ship in self.rest_ships:
            for cell in ship:
                result += '(' + str(cell[0]) + '' + str(cell[1]) + '), '
            result += "\n"

    def print_table(self):
        for i in range(self.size):
            for j in range(self.size):
                print(self.table[i][j], end=' ')
            print('\n')

    def enemy_step(self, cell_0, cell_1):
        cell = (int(cell_0) - 1, int(ord(cell_1) - ord('a')))
        if self.table[cell[0]][cell[1]] == '@' or self.table[cell[0]][cell[1]] == '*' or self.table[cell[0]][cell[1]] == '#':
            logging.info("User reapeated his move")
            if self.table[cell[0]][cell[1]] == '@' or self.table[cell[0]][cell[1]] == '#':
                return "injure \n But you made this move before"
            elif self.table[cell[0]][cell[1]] == '*':
                return "miss \n But you made this move before"
        if self.table[cell[0]][cell[1]] == 2:
            if self.injure_my_ship(cell) == 0:
                answer = "kill"
            else:
                answer = "injure"
            self.table[cell[0]][cell[1]] = '@'
        else:
            answer = "miss"
            self.table[cell[0]][cell[1]] = '*'
        logging.info("user " + answer)
        self.check_win_enemy()
        if self.win_enemy :
            logging.info("User win")
            return answer + "\n" + "You win \n If you want to play again write 'play'"
        cell = self.my_step()
        if cell == (-1,-1):
            return "You made a mistake in your answers"
        self.my_previous_step = cell
        logging.info("Bot chose a cell: (" + str(cell[0]) + ' ' + str(cell[1]) + ")")
        return answer + "\n" + str(cell[0] + 1) + ' ' + str(chr(ord('A') + cell[1]))

    def my_step(self):
        try:
            if self.is_injure:
                return self.find_neighbour_deck()
            else:
                return self.find_ship()
        except:
            logging.info("User made a mistake in his answers")
            return (-1,-1)

    def find_neighbour_deck(self):
        possible_cells = []
        if self.direction_of_last_injure == 0:
            last_injure = self.current_enemy_ship[0]
            if last_injure[0] - 1 >= 0 and self.enemy_table[last_injure[0] - 1][last_injure[1]] == 0:
                possible_cells.append((last_injure[0] - 1, last_injure[1]))
            if last_injure[1] - 1 >= 0 and self.enemy_table[last_injure[0]][last_injure[1] - 1] == 0:
                possible_cells.append((last_injure[0], last_injure[1] - 1))
            if last_injure[0] + 1 < self.size and self.enemy_table[last_injure[0] + 1][last_injure[1]] == 0:
                possible_cells.append((last_injure[0] + 1, last_injure[1]))
            if last_injure[1] + 1 < self.size and self.enemy_table[last_injure[0]][last_injure[1] + 1] == 0:
                possible_cells.append((last_injure[0], last_injure[1] + 1))

        elif self.direction_of_last_injure == 'h':
            minimum = min(self.current_enemy_ship)
            maximum = max(self.current_enemy_ship)
            if minimum[1] - 1 >= 0 and self.enemy_table[minimum[0]][minimum[1] - 1] == 0:
                possible_cells.append((minimum[0], minimum[1] - 1))
            if maximum[1] + 1 < self.size and self.enemy_table[maximum[0]][maximum[1] + 1] == 0:
                possible_cells.append((maximum[0], maximum[1] + 1))

        elif self.direction_of_last_injure == 'v':
            minimum = min(self.current_enemy_ship)
            maximum = max(self.current_enemy_ship)
            if minimum[0] - 1 >= 0 and self.enemy_table[minimum[0] - 1][minimum[1]] == 0:
                possible_cells.append((minimum[0] - 1, minimum[1]))
            if maximum[0] + 1 < self.size and self.enemy_table[maximum[0] + 1][maximum[1]] == 0:
                possible_cells.append((maximum[0] + 1, maximum[1]))

        cell = random.choice(possible_cells)
        self.enemy_rest_cells.remove(cell)
        return cell

    def find_ship(self):
        if self.mode == 'easy':
            return self.find_ship_easy()
        else:
            return self.find_ship_hard()

    def find_ship_easy(self):
        cell = random.choice(self.enemy_rest_cells)
        self.enemy_rest_cells.remove(cell)
        return cell

    def find_ship_hard(self):
        return 0

    def injure_my_ship(self, cell):
        for ship in self.rest_ships:
            if ship.count(cell) > 0:
                ship.remove(cell)
                result = len(ship)
                if result == 0:
                    #for deck in ship :
                    #    self.table[deck[0]][deck[1]] = '#'
                    self.rest_ships.remove(ship)
                return result

    def enemy_answer(self, answer):
        cell = self.my_previous_step

        if answer == 'miss':
            self.enemy_table[cell[0]][cell[1]] = 1
        elif answer == 'injure':
            if len(self.current_enemy_ship) >= max(self.enemy_ships_size) :
                logging.warning("User made a mistake in the answers")
                return "You were wrong somewhere"
            self.is_injure = True
            self.current_enemy_ship.append(cell)
            self.enemy_table[cell[0]][cell[1]] = 2
            self.conclusion_injure(cell)

        else:
            self.current_enemy_ship.append(cell)
            self.enemy_table[cell[0]][cell[1]] = 2
            self.is_injure = False
            self.delete_neighbour()
            self.enemy_ships.append(self.current_enemy_ship)
            if self.enemy_ships_size.count(len(self.current_enemy_ship)) == 0:
                logging.warning("User made a mistake in the answers")
                return "You were wrong somewhere"
            self.enemy_ships_size.remove(len(self.current_enemy_ship))
            self.current_enemy_ship.clear()
            self.direction_of_last_injure = 0
        self.check_win_me()
        if self.win_me:
            logging.info("User lose")
            return "You lose. \n If you want to play again write 'play'"
        return ''

    def delete_neighbour(self):
        all_directions = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (1, 1), (-1, -1), (-1, 1)]
        for deck in self.current_enemy_ship:
            for direction in all_directions:
                cell = (deck[0] + direction[0], deck[1] + direction[1])
                if 0 <= cell[0] < self.size and 0 <= cell[1] < self.size and self.enemy_table[cell[0]][cell[1]] == 0:
                    self.enemy_table[cell[0]][cell[1]] = 1
                    self.enemy_rest_cells.remove(cell)

    def conclusion_injure(self, cell):
        if len(self.current_enemy_ship) == 2:
            direction = (self.current_enemy_ship[0][0] - self.current_enemy_ship[1][0],
                         self.current_enemy_ship[0][1] - self.current_enemy_ship[1][1])
            if direction[0] == 0:
                self.direction_of_last_injure = 'h'
            else:
                self.direction_of_last_injure = 'v'

    def check_win_enemy(self):
        if len(self.rest_ships) == 0:
            self.win_enemy = True

    def check_win_me(self):
        if len(self.enemy_ships) == 10:
            self.win_me = True

    def help(self):
        logging.info("Output of information about the game")
        return "At first, you should put your ships on table size*size. Ships : 1 four-deck, 2 three-deck, " \
               "3 two-deck and 4 one-deck. \n" \
               "defoult size = 10, but if you want to resize table write word 'size' and number > 7 before playing. \n" \
               "Your step is first. You must write me a number from 1 to size and a letter from A to A + size. \n" \
                   "For each of my answers such as '1 A' you have to answer one of the following options: \n " \
                   "'miss', 'injure' or 'kill' \n" \
                   "If you're ready to start write 'Play'"

    def handling_yes_no(self, cmd):
        if cmd.lower() == "yes":
            self.previous_command = cmd.lower()
            logging.info("User want to play")
            return "Let's go! If you want to read information write 'help'\n" \
                   "If you want to resize table write 'size' and number > 7. \n" \
                   "If you're ready to start write 'play' "
        elif cmd.lower() == "no":
            logging.info("User doesn't want to play")
            self.previous_command = cmd.lower()
            return "It's a pity. Good Buy!"
        else:
            logging.warning("Users message is incorrect")
            return "Sorry, I don't understand you. You have to say me yes or no"

    def change_size(self, commands):
        if self.previous_command == "yes":
            if len(commands) > 1:
                cmd2 = commands[1]
            else:
                logging.warning("Users message is incorrect")
                return "It is incorrect message. Try again"

            try:
                test = int(cmd2)
            except ValueError:
                logging.warning("Users message is incorrect")
                return "It is incorrect message. Try again"

            if int(cmd2) > 7:
                self.size = int(cmd2)
                logging.info("Size changed")
                return "Ok"
            else:
                logging.warning("Users message is incorrect")
                return "It is very small size"

        else:
            logging.warning("Users message is incorrect")
            return "You can change size only before playing"

    def handling_cell_selection(self, commands):
        cmd = commands[0]
        if len(commands) > 1:
            cmd2 = commands[1]
        else:
            logging.warning("Users message is incorrect")
            return "It is incorrect message. Try again"
        try:
            if 1 <= int(cmd) <= self.size and "a" <= cmd2.lower() <= chr(ord("a") + self.size - 1):
                self.previous_command = "cell"
                return self.enemy_step(cmd, cmd2.lower())
            else:
                logging.warning("Users message is incorrect")
                return "It is incorrect message. Try again"
        except ValueError:
            logging.warning("Users message is incorrect")
            return "It is incorrect message. Try again"

    def command(self, message):
        logging.info("User message: " + message)
        commands = message.split()
        cmd = commands[0]
        if cmd.lower() == "hi" or cmd.lower() == "hello":
            self.previous_command = "hi"
            return "Hello! \n Do you want to play Seabatttle?"

        elif self.previous_command == "hi":
            return self.handling_yes_no(cmd)

        elif cmd.lower() == "help":
            return self.help()

        elif cmd.lower() == "size":
            return self.change_size(commands)

        elif cmd.lower() == "play":
            try:
                self.previous_command = "play"
                self.start()
                return "Your step is first"
            except:
                logging.error("Can't create table")
                return "Something went wrong"

        elif self.win_me or self.win_enemy:
            logging.warning("Users message is incorrect")
            return "The gave is over. \n If you want to play again write 'play'"

        elif self.previous_command == "play" or self.previous_command == "answer":
            return self.handling_cell_selection(commands)

        elif self.previous_command == "cell":
            if (cmd.lower() == "miss" or cmd.lower() == "injure" or cmd.lower() == "kill") and len(commands) == 1:
                self.previous_command = "answer"
                try:
                    return self.enemy_answer(cmd.lower())
                except:
                    logging.warning("User made a mistake in the answers")
                    return "You were wrong " \
                           "somewhere"
            else:
                logging.warning("Users message is incorrect")
                return "It is incorrect message. Try again"
        elif cmd == "ships":
            return self.print_rest_ships()
        else:
            logging.warning("Users message is incorrect")
            return "It is incorrect message. Try again"
