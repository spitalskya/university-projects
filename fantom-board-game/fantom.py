import mapa
import hrac
import interface
import tkinter


class Program:

    def __init__(self):
        self.interface = interface.Interface(tkinter=tkinter)              # naloaduje sa mapa a interace
        self.board = mapa.Mapa()

        self.agents = []                # zadefinujeme 5 agentov
        for color in ['white', 'blue', 'orange', 'green', 'yellow']:
            self.agents.append(hrac.Agent(color))

        self.phantom = hrac.Phantom()       # inicializujeme Fantoma

        self.interface.canvas.bind('<Button-1>', self.klik)             # canvas z interface, spojime s udalostou klik

        # atributy pre box, kde sa zobrazi fantomova poloha
        self.print_phantom_node_button = self.interface.tkinter.Button(text='Ukáž fantómovu polohu', command=self.show_phantom_node)
        self.print_phantom_node_button.pack()
        self.print_phantom_node_show = False
        self.show_phantom_node()

        self.turn = 1
        self.was_two = False        # ci fantom klikol na dvojity tah

        # self.turn_states = ['ticket', 'move', 'setup']      # stadium kola
        self.turn_state = 'setup'
        self.active_player = 0

        self.clicked_ticket = None
        self.clicked_vertex = None  # vrchol, na ktory bolo kliknute

        self.interface.visual_update(self.agents[self.active_player], self.turn, self.turn_state)

        tkinter.mainloop()

    def klik(self, event):
        x = event.x
        y = event.y

        self.clicked_action(x, y)

    def show_phantom_node(self):
        self.interface.print_phantom_node(self.phantom, self.print_phantom_node_show)
        if self.print_phantom_node_show:
            self.print_phantom_node_show = False
        else:
            self.print_phantom_node_show = True

    def clicked_action(self, x, y):
        if self.turn_state == 'ticket':
            for ticket in (self.board.bus, self.board.tram, self.board.taxi, self.board.sail, self.board.two):
                xt = self.interface.transport_coords[ticket][0]
                yt = self.interface.transport_coords[ticket][1]

                if ((xt - x) ** 2 + (yt - y) ** 2) ** 0.5 <= 50:
                    self.clicked_ticket = ticket
                    break

                if ticket == 2 and isinstance(self.active_player, int):     # iba fantom ma k dispozicii dalsie listky
                    break

            if self.clicked_ticket is None:
                if self.active_player == 'phantom':
                    self.interface.visual_update(self.phantom, self.turn, 'no_ticket')
                    if self.was_two:
                        self.interface.color_transport(self.board.two)
                else:
                    self.interface.visual_update(self.agents[self.active_player], self.turn, 'no_ticket')
            else:
                self.interface.color_transport(self.clicked_ticket)

                if self.active_player != 'phantom':
                    self.phantom.tickets[ticket] += 1           # fantom dostava listky od agentov

                if self.clicked_ticket == 4:                # vyriesenie double move
                    self.was_two = True
                    self.interface.show_phantom_ticket(self.clicked_ticket)
                    self.phantom.tickets[self.board.two] -= 1

                if self.was_two and self.clicked_ticket != 4:    # ak je v double move, ide sa hybat s novym listkom
                    self.turn_state = 'move'
                elif self.was_two:                          # ak klikol na double move, vybera listok znova
                    self.turn_state = 'ticket'
                    self.interface.animation_timer = False
                else:
                    self.turn_state = 'move'

                if self.active_player == 'phantom':
                    self.interface.visual_update(self.phantom, self.turn, self.turn_state)
                    if self.was_two:
                        self.interface.color_transport(self.board.two)

                else:
                    self.interface.visual_update(self.agents[self.active_player], self.turn, self.turn_state)

        elif self.turn_state == 'move':
            for node in self.interface.nodes_coords:  # prejdeme vsetky suradnice vrcholov, hladame blizky vrchol
                xn = node[1][0] + self.interface.shift
                yn = node[1][1] + self.interface.shift

                if ((xn - x) ** 2 + (yn - y) ** 2) ** 0.5 <= 10:
                    self.clicked_vertex = node[0]
                    break
            else:
                # ak neklikne na vrchol, pozrieme sa, ci neklikol na transport,
                # ak ano, zavola sa funkcia znova vo faze ticket
                for ticket in (self.board.bus, self.board.tram, self.board.taxi, self.board.sail, self.board.two):
                    xt = self.interface.transport_coords[ticket][0]
                    yt = self.interface.transport_coords[ticket][1]

                    if ((xt - x) ** 2 + (yt - y) ** 2) ** 0.5 <= 50:
                        self.clicked_ticket = ticket
                        break

                    if ticket == 2 and self.active_player != 'phantom':  # iba fantom ma k dispozicii dalsie listky
                        break

                if self.clicked_ticket is not None:
                    self.turn_state = 'ticket'

                    self.interface.uncolor_transport(additional=True)
                    if self.was_two:
                        self.interface.color_transport(self.board.two)

                    self.clicked_action(x, y)
                    return

            if self.active_player == 'phantom':
                legal = self.phantom.move(self.clicked_vertex, self.clicked_ticket, self.board)

                if legal:
                    self.interface.move_phantom(self.phantom, self.turn)

                    if self.turn in self.phantom.show_phantom:      # ukaze sa, aky listok pouzil, popripade aj miesto
                        self.interface.show_phantom_ticket(self.clicked_ticket, self.clicked_vertex)
                    else:
                        self.interface.show_phantom_ticket(self.clicked_ticket)

                    if self.was_two:                # preskocime agentov
                        self.active_player = 'phantom'
                        self.turn += 1
                        self.was_two = False
                    else:
                        self.active_player = 0
            else:
                legal = self.agents[self.active_player].move(self.clicked_vertex, self.clicked_ticket, self.board)
                if legal:
                    self.interface.move_agent(self.agents[self.active_player])

                    if self.active_player == 4:  # cyklujeme cez agentov, ak sme na poslednom, prejde kolo na fantoma
                        self.active_player = 'phantom'
                        self.turn += 1
                    else:
                        self.active_player += 1

            if legal:
                self.check_win()
                self.turn_state = 'ticket'
                self.interface.uncolor_transport()

                if self.active_player == 'phantom':
                    self.interface.visual_update(self.phantom, self.turn, self.turn_state)
                else:
                    self.interface.visual_update(self.agents[self.active_player], self.turn, self.turn_state)

                self.clicked_ticket = None
                self.clicked_vertex = None
            else:
                if self.active_player == 'phantom':
                    self.interface.visual_update(self.phantom, self.turn, 'no_path')
                else:
                    self.interface.visual_update(self.agents[self.active_player], self.turn, 'no_path')

        elif self.turn_state == 'setup':
            for node in self.interface.nodes_coords:  # prejdeme vsetky suradnice vrcholov, hladame blizky vrchol
                xn = node[1][0] + self.interface.shift
                yn = node[1][1] + self.interface.shift

                if ((xn - x) ** 2 + (yn - y) ** 2) ** 0.5 <= 10:
                    self.clicked_vertex = node[0]
                    break

            if self.active_player == 'phantom':
                legal = self.phantom.place(self.clicked_vertex)
                if legal:
                    self.interface.place_phantom(self.phantom)
            else:
                legal = self.agents[self.active_player].place(self.clicked_vertex)
                if legal:
                    self.interface.place_agent(self.agents[self.active_player])

            self.clicked_vertex = None

            if legal:
                if self.active_player == 4:
                    self.active_player = 'phantom'
                elif self.active_player != 'phantom':
                    self.active_player += 1
                elif self.active_player == 'phantom':
                    self.turn_state = 'ticket'
                    self.turn += 1
                    self.interface.visual_update(self.phantom, self.turn, 'end_setup')  # aby sa zobrazili ikony listkov
                    self.interface.visual_update(self.phantom, self.turn, self.turn_state)
                # phantom sa posledny umiestni a prvy taha

                if self.active_player == 'phantom':
                    self.interface.visual_update(self.phantom, self.turn, self.turn_state)
                else:
                    self.interface.visual_update(self.agents[self.active_player], self.turn, self.turn_state)
            else:
                if self.active_player == 'phantom':
                    self.interface.visual_update(self.phantom, self.turn, 'no_node')
                else:
                    self.interface.visual_update(self.agents[self.active_player], self.turn, 'no_node')

    def check_win(self):    # overenie, ci niektory tim nevyhral
        for agent in self.agents:
            if agent.position == self.phantom.position:
                self.interface.win_screen('agents')
                break
        else:
            if self.turn == 24 and self.active_player == 4:
                self.interface.win_screen('phantom')


Program()
