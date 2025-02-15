from PIL import Image, ImageTk

class Interface:

    def __init__(self, tkinter):
        self.shift = 30  # o kolko je posunuta mapa oproti 0, 0

        self.tkinter = tkinter
        self.canvas = self.tkinter.Canvas(width=1800, height=885 + 2 * self.shift, bg='#E54714')
        self.canvas.pack()

        self.insert_photo('table.png', 0, 0, anchor='nw', tag='table')  # pridanie stola a mapy
        self.insert_photo('mapa-draft2.png', self.shift, self.shift, anchor='nw', tag='map')

        # obrazky prostriedkov
        self.transport_coords = [(1300, 350), (1400, 350), (1500, 350), (1350, 525), (1450, 525)]
        self.generate_transport_icons()

        # obdlznik, kde sa ukazuje aktivny hrac
        self.generate_active_player_area()

        # pocitac kol
        self.canvas.create_text(1800 - 2 * self.shift, 885, text='', font=("Arial", 30, 'bold'), tag='turn-counter')

        self.nodes_coords = self.load_nodes_coordinates()

        self.phantom_label_box = tkinter.Label(text='')
        self.phantom_label_box.pack()

        self.phantoms_tickets_x = 1100
        self.phantoms_tickets_y = 680

        self.win = False

        self.animation = None
        self.animation_timer = False             # co je timer spusteny (bude iba jedna animacia naraz)

    def generate_active_player_area(self):
        x1 = 950 + self.shift
        y1 = 50
        x2 = 1730 + self.shift
        y2 = 250

        self.canvas.create_rectangle(x1, y1, x2, y2, fill='', tag='active-player-area',
                                     outline='')
        self.canvas.create_text((x1 + x2) // 2, y1 * 0.75 + y2 * 0.25, text='', fill='', font=("Arial", 40, 'bold'),
                                tag='active-player-text')
        self.canvas.create_text((x1 + x2) // 2, y1 * 0.25 + y2 * 0.75, text='', fill='', font=("Arial", 40, 'bold'),
                                tag='active-player-action')

    def generate_transport_icons(self):
        for i, transport in enumerate(('bus', 'tram', 'taxi', 'sail', 'two')):
            self.insert_photo(f'prostriedky/{transport}-colored.png', self.transport_coords[i][0],
                              self.transport_coords[i][1],
                              tag=f'{transport}-color')
            self.canvas.itemconfig(f'{transport}-color', state='hidden')
            self.insert_photo(f'prostriedky/{transport}.png', self.transport_coords[i][0], self.transport_coords[i][1],
                              tag=f'{transport}')
            self.canvas.create_text(self.transport_coords[i][0], self.transport_coords[i][1] + 80, text='',
                                    font=("Arial", 40, 'bold'), tag=f'{transport}-tickets')

    '''
    def color_transport(self, ticket):
        for i, transport in enumerate(('bus', 'tram', 'taxi', 'sail', 'two')):
            if i == ticket:
                self.canvas.itemconfig(f'{transport}-color', state='normal')
                self.canvas.itemconfig(f'{transport}', state='hidden')
    '''

    def color_transport(self, ticket):
        for i, transport in enumerate(('bus', 'tram', 'taxi', 'sail')):
            if i == ticket:
                obr = Image.open(f'images/prostriedky/{transport}-animated.png')
                sir, vys = obr.width // 16, obr.height
                images = []
                for x in range(0, obr.width, sir):
                    images.append(ImageTk.PhotoImage(obr.crop((x, 0, x + sir, vys))))

                self.animation = Animate(self.transport_coords[i][0], self.transport_coords[i][1], images, self.canvas)
                if not self.animation_timer: self.timer()

                self.canvas.itemconfig(f'{transport}', state='hidden')
                break
        else:
            self.canvas.itemconfig('two-color', state='normal')
            self.canvas.itemconfig('two', state='hidden')

    def timer(self):
        if self.animation is None: return

        self.animation_timer = True
        self.animation.next_phase()
        self.canvas.after(100, self.timer)

    def uncolor_transport(self, additional=False):
        if self.win: return

        for transport in ('bus', 'tram', 'taxi', 'sail', 'two'):
            self.canvas.itemconfig(f'{transport}-color', state='hidden')
            self.canvas.itemconfig(f'{transport}', state='normal')

            if not additional: self.animation_timer = False
        self.animation = None

    def place_agent(self, agent):
        color = agent.tag
        node = agent.position

        x = self.nodes_coords[node - 1][1][0] + self.shift
        y = self.nodes_coords[node - 1][1][1] + self.shift - 15
        self.insert_photo(f'pawns/{color}-small.png', x, y, tag=color)

    def move_agent(self, agent):
        color = agent.tag
        node = agent.position

        x = self.nodes_coords[node - 1][1][0] + self.shift
        y = self.nodes_coords[node - 1][1][1] + self.shift - 15
        self.canvas.coords(color, x, y)

    def place_phantom(self, phantom):
        color = phantom.tag
        node = phantom.position

        x = self.nodes_coords[node - 1][1][0] + self.shift
        y = self.nodes_coords[node - 1][1][1] + self.shift - 15
        self.insert_photo(f'pawns/{color}-small.png', x, y, tag=color)
        self.canvas.itemconfig(color, state='hidden')

        self.insert_photo(f'pawns/{color}-small.png', x, y, tag=f'{color}-copy')  # na zobrazovanie v urcitych tahoch
        self.canvas.itemconfig('black-copy', state='hidden')

    def move_phantom(self, phantom, turn):
        color = phantom.tag
        node = phantom.position

        x = self.nodes_coords[node - 1][1][0] + self.shift
        y = self.nodes_coords[node - 1][1][1] + self.shift - 15
        self.canvas.coords(color, x, y)

        if turn in phantom.show_phantom:
            # zobrazi sa figurka tam, kde stoji fantom, ostane tam do dalsieho doleziteho tahu
            self.canvas.coords('black-copy', x, y)
            self.canvas.itemconfig('black-copy', state='normal')

    def show_phantom_ticket(self, ticket, node=None):
        for i, transport in enumerate(('bus', 'tram', 'taxi', 'sail', 'two')):
            if i == ticket:
                self.insert_photo(f'prostriedky/{transport}-small.png', self.phantoms_tickets_x,
                                  self.phantoms_tickets_y, tag='phantom-history')
                self.phantoms_tickets_x += 75
                if self.phantoms_tickets_x > 1700:
                    self.phantoms_tickets_x = 1100
                    self.phantoms_tickets_y += 55

        if node is not None:
            self.canvas.create_text(self.phantoms_tickets_x, self.phantoms_tickets_y, text=node,
                                    font=("Arial", 30, 'bold'), tag='phantom-history')
            self.phantoms_tickets_x += 75
            if self.phantoms_tickets_x > 1700:
                self.phantoms_tickets_x = 1100
                self.phantoms_tickets_y += 55

    def print_phantom_node(self, phantom, show):
        if show:
            self.phantom_label_box['text'] = phantom.position
        else:
            self.phantom_label_box['text'] = ''

    def insert_photo(self, img_name, x, y, anchor='center', tag=None):
        self.tmp_img = self.tkinter.PhotoImage(file=f'images/{img_name}')

        self.tmp_label = self.tkinter.Label(image=self.tmp_img)
        self.tmp_label.image = self.tmp_img                     # zachovanie referencie
        # self.label.pack()

        self.canvas.create_image(x, y, image=self.tmp_img, anchor=anchor, tag=tag)

    def load_nodes_coordinates(self):
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
        return sur

    def visual_update(self, active_player, turn, action):  # DOROBIT WIN SCREEN
        if self.win: return

        if action == 'setup':  # pocas setupu sa nemaju zobrazovat ikony listkov
            for transport in ('bus', 'tram', 'taxi', 'sail', 'two'):
                self.canvas.itemconfig(f'{transport}-color', state='hidden')
                self.canvas.itemconfig(f'{transport}', state='hidden')
                self.canvas.itemconfig(f'{transport}-tickets', state='hidden')
        elif action == 'end_setup':
            for transport in ('bus', 'tram', 'taxi', 'sail', 'two'):  # ked skonci setup, zobrazia sa listky
                self.canvas.itemconfig(f'{transport}-color', state='hidden')
                self.canvas.itemconfig(f'{transport}', state='normal')
                self.canvas.itemconfig(f'{transport}-tickets', state='normal')
        elif action == 'ticket':  # ak hra fantom, zobrazia sa mu listky
            for transport in ('sail', 'two'):
                self.canvas.itemconfig(f'{transport}-color', state='hidden')
                self.canvas.itemconfig(f'{transport}', state='normal')
                self.canvas.itemconfig(f'{transport}-tickets', state='normal')
        elif action == 'no_path':
            self.canvas.itemconfig('active-player-action', text='Taká cesta neexistuje')
        elif action == 'no_node':
            self.canvas.itemconfig('active-player-action', text='Klikni na vyznačené miesto')
        elif action == 'no_ticket':
            self.canvas.itemconfig('active-player-action', text='Klikni na ikonu transportu')

        if active_player.tag != 'black':  # ak nehra fantom, odstrania sa dva specialne listky
            for transport in ('sail', 'two'):
                self.canvas.itemconfig(f'{transport}-color', state='hidden')
                self.canvas.itemconfig(f'{transport}', state='hidden')
                self.canvas.itemconfig(f'{transport}-tickets', state='hidden')

        # zobrazenie poctu listkov
        for transport, ticket in tuple(zip(('bus', 'tram', 'taxi', 'sail', 'two'), active_player.tickets)):
            self.canvas.itemconfig(f'{transport}-tickets', text=ticket)

        # zobrazenie kto je na tahu a co ma robit
        for player_tag, farba in tuple(zip(('black', 'white', 'blue', 'orange', 'green', 'yellow'),
                                           ('fantóm', 'biely', 'modrý', 'oranžový', 'zelený', 'žltý'))):
            if active_player.tag == player_tag:
                if player_tag in ('white', 'yellow'):
                    self.canvas.itemconfig('active-player-text', text=f'Na ťahu je {farba}', fill='black')
                    if action == 'ticket':
                        self.canvas.itemconfig('active-player-action', text=f'Zvoľ si lístok', fill='black')
                    elif action == 'move':
                        self.canvas.itemconfig('active-player-action', text=f'Zvoľ kam ideš', fill='black')
                    elif action == 'setup':
                        self.canvas.itemconfig('active-player-action', text=f'Umiestni svoju figúrku', fill='black')

                else:
                    self.canvas.itemconfig('active-player-text', text=f'Na ťahu je {farba}', fill='white')
                    if action == 'ticket':
                        self.canvas.itemconfig('active-player-action', text=f'Zvoľ si lístok', fill='white')
                    elif action == 'move':
                        self.canvas.itemconfig('active-player-action', text=f'Zvoľ kam ideš', fill='white')
                    elif action == 'setup':
                        self.canvas.itemconfig('active-player-action', text=f'Umiestni svoju figúrku', fill='white')

                self.canvas.itemconfig('active-player-area', fill=f'{player_tag}')

        # zobrazenie kola
        self.canvas.itemconfig('turn-counter', text=f'{turn}')

    def win_screen(self, which):
        self.uncolor_transport()
        self.win = True

        tags = ['active-player-area', 'active-player-text', 'active-player-action', 'turn-counter', 'phantom-history']
        transports = ['bus', 'tram', 'taxi', 'sail', 'two']

        for tag in tags:
            self.canvas.itemconfig(tag, state='hidden')
        for transport in transports:
            self.canvas.itemconfig(f'{transport}', state='hidden')
            self.canvas.itemconfig(f'{transport}-color', state='hidden')
            self.canvas.itemconfig(f'{transport}-tickets', state='hidden')

        self.insert_photo('trophy.png', 1370, 450)

        if which == 'agents':
            self.canvas.create_text(1370, 325, text=f'Vyhrali\nagenti', font=("Arial", 40, 'bold'), justify='center')
        else:
            self.canvas.create_text(1370, 325, text=f'Vyhral\nfantóm', font=("Arial", 40, 'bold'), justiy='center')

        self.canvas.itemconfig('black', state='normal')
        self.canvas.itemconfig('black-copy', state='hidden')

        self.canvas.unbind('<Button-1>')


class Animate:
    def __init__(self, x, y, images, canvas):
        self.canvas = canvas
        self.id = self.canvas.create_image(x, y)
        self.images = images
        self.phase = 0

    def next_phase(self):
        self.phase = (self.phase + 1) % len(self.images)
        self.canvas.itemconfig(self.id, image=self.images[self.phase])


if __name__ == '__main__':
    import tkinter

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

    Interface(tkinter=tkinter)
    tkinter.mainloop()
