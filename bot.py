import random


class Robot:
    def __init__(self, _size=10):
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


    def Start(self):
        self.GenerateTable()
        self.enemy_table = [[0] * self.size for i in range(self.size)]
        self.enemy_rest_cells = [(i, j) for i in range(0, self.size) for j in range(0, self.size)]


    def GenerateTable(self):
        my_table = [[0] * self.size for i in range(self.size)]
        free_cells = [(i, j) for i in range(0, self.size) for j in range(0, self.size)]

        # ставим корабли
        self.GenerateShip(free_cells, my_table, 4)
        self.GenerateShip(free_cells, my_table, 3)
        self.GenerateShip(free_cells, my_table, 3)
        self.GenerateShip(free_cells, my_table, 2)
        self.GenerateShip(free_cells, my_table, 2)
        self.GenerateShip(free_cells, my_table, 2)
        self.GenerateShip(free_cells, my_table, 1)
        self.GenerateShip(free_cells, my_table, 1)
        self.GenerateShip(free_cells, my_table, 1)
        self.GenerateShip(free_cells, my_table, 1)

        self.table = my_table

    def GenerateShip(self, free_cells, my_table, size_ship):
        # будем рассматривать только 2 направления от выбранной клетки - вниз и вправо
        ship_put = False
        while not ship_put:

            curr_cell = random.choice(free_cells)
            correct_directions = []
            if curr_cell[0] + size_ship <= self.size:
                correct_directions.append((1, 0))

            if curr_cell[1] + size_ship <= self.size:
                correct_directions.append((0, 1))

            if (len(correct_directions) > 0):
                direction = random.choice(correct_directions)

                # проверяем, что в выбранном направлении можем поставить корабль
                i = 1
                success = True
                while (i < size_ship and success):
                    if (free_cells.count((curr_cell[0] + i * direction[0], curr_cell[1] + i * direction[1])) == 0):
                        success = False
                    i += 1

                if success == True:
                    ship_put = True

        current_ship = []
        for k in range(size_ship):
            current_ship.append((curr_cell[0], curr_cell[1]))
            my_table[curr_cell[0]][curr_cell[1]] = 2
            self.DeleteUsedCells(free_cells, curr_cell)
            curr_cell = (curr_cell[0] + direction[0], curr_cell[1] + direction[1])

        self.ships.append(current_ship)
        self.rest_ships.append(current_ship)

    def DeleteUsedCells(self, free_cells, curr_cell):
        all_directions = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (1, 1), (-1, -1), (-1, 1)]
        for direction in all_directions:
            cell = (curr_cell[0] + direction[0], curr_cell[1] + direction[1])
            if free_cells.count(cell) > 0:
                free_cells.remove(cell)

    def PrintTable(self):
        for i in range(self.size):
            for j in range(self.size):
                print(self.table[i][j], end=' ')
            print('\n')

    def Play(self, cell_0, cell_1):
        self.MyStep()
        self.CheckWinMe()


    def EnemyStep(self, cell_0, cell_1):
        cell = (int(cell_0) - 1, int(ord(cell_1) - ord('a')))
        if self.table[cell[0]][cell[1]] == 2:
            if self.InjureMyShip(cell) == 0:
                answer = "kill"
            else:
                answer = "injure"
            self.table[cell[0]][cell[1]] = '@'
        else:
            answer = "miss"
            self.table[cell[0]][cell[1]] = '*'
        self.CheckWinEnemy()
        if self.win_enemy :
            return answer + "\n" + "You win"
        cell = self.MyStep()
        self.my_previous_step = cell
        return answer + "\n" + str(cell[0] + 1) + ' ' +  str(chr(ord('A') + cell[1]))

    def MyStep(self):
        if self.is_injure == True:
            return self.FindNeighbourDeck()
        else:
            return self.FindShip()


    def FindNeighbourDeck(self):
        possible_cells = []
        if self.direction_of_last_injure == 0:
            last_injure = self.current_enemy_ship[0]
            if (last_injure[0] - 1 >= 0 and self.enemy_table[last_injure[0] - 1][last_injure[1]] == 0):
                possible_cells.append((last_injure[0] - 1, last_injure[1]))
            if (last_injure[1] - 1 >= 0 and self.enemy_table[last_injure[0]][last_injure[1] - 1] == 0):
                possible_cells.append((last_injure[0], last_injure[1] - 1))
            if (last_injure[0] + 1 < self.size and self.enemy_table[last_injure[0] + 1][last_injure[1]] == 0):
                possible_cells.append((last_injure[0] + 1, last_injure[1]))
            if (last_injure[1] + 1 < self.size and self.enemy_table[last_injure[0]][last_injure[1] + 1] == 0):
                possible_cells.append((last_injure[0], last_injure[1] + 1))

        elif self.direction_of_last_injure == 'h':
            minimum = min(self.current_enemy_ship)
            maximum = max(self.current_enemy_ship)
            if (minimum[1] - 1 >= 0 and self.enemy_table[minimum[0]][minimum[1] - 1] == 0):
                possible_cells.append((minimum[0], minimum[1] - 1))
            if (maximum[1] + 1 < self.size and self.enemy_table[maximum[0]][maximum[1] + 1] == 0):
                possible_cells.append((maximum[0], maximum[1] + 1))

        elif self.direction_of_last_injure == 'v':
            minimum = min(self.current_enemy_ship)
            maximum = max(self.current_enemy_ship)
            if (minimum[0] - 1 >= 0 and self.enemy_table[minimum[0] - 1][minimum[1]] == 0):
                possible_cells.append((minimum[0] - 1, minimum[1]))
            if (maximum[0] + 1 < self.size and self.enemy_table[maximum[0] + 1][maximum[1]] == 0):
                possible_cells.append((maximum[0] + 1, maximum[1]))

        cell = random.choice(possible_cells)
        self.enemy_rest_cells.remove(cell)
        return cell

    def FindShip(self):
        if self.mode == 'easy':
            return self.FindShipEasy()
        else:
            return self.FindShipHard()

    def FindShipEasy(self):
        cell = random.choice(self.enemy_rest_cells)
        self.enemy_rest_cells.remove(cell)
        return cell

    def FindShipHard(self):
        return 0

    def InjureMyShip(self, cell):
        for ship in self.rest_ships:
            if ship.count(cell) > 0:
                ship.remove(cell)
                result = len(ship)
                if result == 0:
                    for deck in ship :
                        self.table[deck[0]][deck[1]] = '#'
                    self.rest_ships.remove(ship)
                return result

    def EnemyAnswer(self, answer):
        cell = self.my_previous_step

        if answer == 'miss':
            self.enemy_table[cell[0]][cell[1]] = 1
        elif answer == 'injure':
            self.is_injure = True
            self.current_enemy_ship.append(cell)
            self.enemy_table[cell[0]][cell[1]] = 2
            self.ConclusionInjure(cell)

        else:
            self.current_enemy_ship.append(cell)
            self.enemy_table[cell[0]][cell[1]] = 2
            self.is_injure = False
            self.DeleteNeighbour()
            self.enemy_ships.append(self.current_enemy_ship)
            self.current_enemy_ship.clear()
            self.direction_of_last_injure = 0
        self.CheckWinMe()
        if self.win_me:
            return "You lose"
        return ''

    def DeleteNeighbour(self):
        all_directions = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (1, 1), (-1, -1), (-1, 1)]
        for deck in self.current_enemy_ship:
            for direction in all_directions:
                cell = (deck[0] + direction[0], deck[1] + direction[1])
                if (0 <= cell[0] < self.size and 0 <= cell[1] < self.size and self.enemy_table[cell[0]][cell[1]] == 0):
                    self.enemy_table[cell[0]][cell[1]] = 1
                    self.enemy_rest_cells.remove(cell)

    def ConclusionInjure(self, cell):
        if len(self.current_enemy_ship) == 2:
            direction = (self.current_enemy_ship[0][0] - self.current_enemy_ship[1][0],
                         self.current_enemy_ship[0][1] - self.current_enemy_ship[1][1])
            if direction[0] == 0:
                self.direction_of_last_injure = 'h'
            else:
                self.direction_of_last_injure = 'v'

    def CheckWinEnemy(self):
        if len(self.rest_ships) == 0:
            self.win_enemy = True


    def CheckWinMe(self):
        if len(self.enemy_ships) == 10:
            self.win_me = True

    def Help(self):
        return "At first, you should put your ships on table size*size. Ships : 1 four-deck, 2 three-deck, 3 two-deck and 4 one-deck. \n" \
               "defoult size = 10, but if you want to resize table write word 'size' and number > 7 before playing. \n" \
               "Your step is first. You must write me a number from 1 to size and a letter from A to A + size. \n" \
                   "For each of my answers such as '1 A' you have to answer one of the following options: \n " \
                   "'miss', 'injure' or 'kill' \n" \
                   "If you're ready to start write 'Play'"

    def command(self, message):
        commands = message.split()
        cmd = commands[0]
        if cmd.lower() == "hi" or cmd.lower() == "hello":
            self.previous_command = "hi"
            return "Hello! \n Do you want to play Seabatttle?"

        elif self.previous_command == "hi" :
            if cmd.lower() == "yes" :
                self.previous_command = cmd.lower()
                return "Let's go! If you want to read information write 'help'\n"\
                       "If you want to resize table write 'size' and number > 7. \n" \
                       "If you're ready to start write 'play' "
            elif cmd.lower() == "no":
                self.previous_command = cmd.lower()
                return "It's a pity. Good Buy!"
            else :
                return "Sorry, I don't understand you. You have to say me yes or no"

        elif cmd.lower() == "help" :
            return self.Help()

        elif cmd.lower() == "size":
            if self.previous_command == "yes" :
                if (len(commands) > 1):
                    cmd2 = commands[1]
                else:
                    return "It is incorrect message. Try again"
                if int(cmd2) >= 7 :
                    self.size = int(cmd2)
                    return "Ok"
                else:
                    return "It is very small size"

        elif cmd.lower() == "play" :
            self.previous_command = "play"
            self.Start()
            return "Your step is first"

        elif self.previous_command == "play" or self.previous_command == "answer":
            if(len(commands) > 1) :
                cmd2 = commands[1]
            else :
                return "It is incorrect message. Try again"
            if 1 <= int(cmd) <= self.size and "a" <= cmd2.lower() <= chr(ord("a") + self.size - 1) :
                self.previous_command = "cell"
                return self.EnemyStep(cmd, cmd2.lower())
            else :
                return "It is incorrect message. Try again"

        elif self.previous_command == "cell" :
            if cmd.lower() == "miss"  or cmd.lower() == "injure" or cmd.lower() == "kill" :
                self.previous_command = "answer"
                self.EnemyAnswer(cmd.lower())
            else :
                return "It is incorrect message. Try again"
