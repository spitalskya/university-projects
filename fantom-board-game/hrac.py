class Agent:

    def __init__(self, tag):
        self.tag = tag

        self.position = None
        self.tickets = [10, 9, 5]           # bus, taxi, tram

    def place(self, node):
        try:
            if node > 202:
                self.invalid_move('node')
                return False
            self.position = node
            return True
        except TypeError:
            self.invalid_move('node')
            return False

    def move(self, to, way, plocha):
        try:
            if to > 202:
                self.invalid_move('node')
                return False
        except TypeError:
            return False

        try:
            if plocha.exists_path(self.position, to, way) and self.tickets[way] > 0:
                self.position = to
                self.tickets[way] -= 1
                return True

            else:
                if plocha.exists_path(self.position, to, way):
                    self.invalid_move('ticket')
                else:
                    self.invalid_move('path')
                return False
        except IndexError:
            self.invalid_move('ticket')
            return False

    def invalid_move(self, cause, debug=False):
        if not debug: return

        if cause == 'path':
            print('No path')
        elif cause == 'ticket':
            print('No ticket')
        elif cause == 'node':
            print('No such node')
        else:
            print('Invalid move')


class Phantom:

    def __init__(self, tag='black'):
        self.tag = tag

        self.position = None
        self.tickets = [4, 3, 3, 2, 2]  # bus, taxi, tram, sail, double

        self.show_phantom = [3, 8, 13, 18, 24]  # kola, kedy sa fantom ukaze

    def place(self, node):
        try:
            if node > 202:
                self.invalid_move('node')
                return False
            self.position = node
            return True
        except TypeError:
            self.invalid_move('node')

    def move(self, to, way, plocha):
        try:
            if to > 202:
                self.invalid_move('node')
                return False
        except TypeError:
            self.invalid_move('node')
            return False
        try:
            if plocha.exists_path(self.position, to, way) and self.tickets[way] > 0:
                self.position = to
                self.tickets[way] -= 1
                return True
            else:
                if plocha.exists_path(self.position, to, way):
                    self.invalid_move('ticket')
                    return False
                else:
                    self.invalid_move('path')
                    return False
        except IndexError:
            self.invalid_move('ticket')
            return False

    def invalid_move(self, cause, debug=False):
        if not debug: return

        if cause == 'path':
            print('No path')
        elif cause == 'ticket':
            print('No ticket')
        elif cause == 'node':
            print('No such node')
        else:
            print('Invalid move')


if __name__ == '__main__':
    import tkinter
    import mapa


    def inputer():
        a = input('Zadaj pohyb: ')

        node, way = a.split()
        node = int(node)

        red.move(int(node), int(way))
        print(red.position)
        print(red.tickets)

        canvas.after(100, inputer)

    sur = []
    with open('suradnice_bodov.txt', 'r') as file:
        subor = file.read()

    subor = subor[:-1].split('\n')

    for line in subor:
        line = line.split()
        vertex, coords_x, coords_y = line[0], line[1], line[2]

        vertex = int(vertex[1:-1])
        coords_x = int(coords_x[1:-1])
        coords_y = int(coords_y[:-2])

        sur.append((vertex, (coords_x, coords_y)))

    win = tkinter.Tk()
    pozadie = tkinter.PhotoImage(file='images/mapa-draft1.png')
    sir, vys = pozadie.width(), pozadie.height()
    canvas = tkinter.Canvas(width=sir, height=vys)
    canvas.pack()
    canvas.create_image(0, 0, image=pozadie, anchor='nw')

    plocha = mapa.Mapa()

    red = Agent('red')
    red.place(99)

    canvas.after(100, inputer)

    tkinter.mainloop()
