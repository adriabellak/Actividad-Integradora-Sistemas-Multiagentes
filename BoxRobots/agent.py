from mesa import Agent, agent

class Box(Agent):
    """
    Boxes that are going to be picked up by the robots
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos

    def step(self):
        pass

class Obstacle(Agent):
    """
    Walls that limit the room
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Robot(Agent):
    """
    Robots that will be picking up boxes
    """

    def __init__(self, unique_id, model, _drop_zone):
        """
        Crea un robotin nuevo
        """
        super().__init__(unique_id, model)
        self.direction = 2
        self.condition = "free"
        self.moves = 0
        self.visited = []
        self.found_boxes = []
        self.drop_zone =  _drop_zone
        self.movements = 0

    def gradient(self, possible_steps, p2):
        minimum = 10000
        # minimum = abs(possible_steps[2][0] - p2[0]) + abs(possible_steps[2][1] - p2[1])
        direction = possible_steps[2]
        for step in range(0, len(possible_steps)):
            gradient = abs(possible_steps[step][0] - p2[0]) + abs(possible_steps[step][1] - p2[1])
            agent = self.model.grid.get_cell_list_contents(possible_steps[step])
            if gradient == 0:
                direction = possible_steps[step]
                return direction
            elif agent != []:
                agent = agent[0]
                if isinstance(agent, Box):
                    if possible_steps[step] not in self.found_boxes:
                        self.found_boxes.append(possible_steps[step])
            elif (possible_steps[step] not in self.visited):
                if gradient < minimum: 
                    minimum = gradient
                    direction = possible_steps[step]

        if minimum == 10000:
            for step in range(0, len(possible_steps)):
                gradient = abs(possible_steps[step][0] - p2[0]) + abs(possible_steps[step][1] - p2[1])
                agent = self.model.grid.get_cell_list_contents(possible_steps[step])
                if agent == []:
                    if gradient < minimum: 
                        minimum = gradient
                        direction = possible_steps[step]
            if minimum == 10000:
                return possible_steps[2]

        return direction

    def move(self, possible_steps):
        visited_neighbors = 0
        for step in possible_steps:
            if step in self.visited:
                visited_neighbors += 1
            agent = self.model.grid.get_cell_list_contents(step)
            if agent == []:
                if step not in self.visited:
                    return step
            elif isinstance(agent[0], Box):
                if step not in self.found_boxes:
                    self.found_boxes.append(step)

        for step in possible_steps:
            agent = self.model.grid.get_cell_list_contents(step)
            if agent == []:
                self.visited.clear()
                return step

        return possible_steps[2]

    def pick_up(self, pos, box):
        self.model.grid.remove_agent(box)
        self.movements += 1
        self.model.grid.move_agent(self, pos)
        self.visited.clear()
        self.condition = "loaded"

    def drop_box(self):
        self.condition = "free"
        self.visited = []
        self.model.boxes_left -= 1

        self.found_boxes.pop(0)

    def step(self):
        """ 
        Determines the plan that the robot is going to be executing
        """
        self.visited.append(self.pos)
        # print("Box queue:", self.found_boxes)
        possible_steps = [
            (self.pos[0]+1, self.pos[1]),
            (self.pos[0], self.pos[1]+1),
            (self.pos[0], self.pos[1]),
            (self.pos[0]-1, self.pos[1]),
            (self.pos[0], self.pos[1]-1)
        ]

        if self.condition == "free":
            if len(self.found_boxes) > 0:
                self.direction = self.gradient(possible_steps, self.found_boxes[0
                ])
                # and isinstance(self.model.grid.get_cell_list_contents(self.direction)[0], Box)
                if self.model.grid.get_cell_list_contents(self.direction) != [] and isinstance(self.model.grid.get_cell_list_contents(self.direction)[0], Box):
                    self.pick_up(self.direction, self.model.grid.get_cell_list_contents(self.direction)[0])
                    print("picking up", self.direction)
                    # self.pick_up(self.direction)
                elif self.model.grid.get_cell_list_contents(self.direction) != [] and isinstance(self.model.grid.get_cell_list_contents(self.direction)[0], Robot):
                    self.found_boxes.pop(0)
                else:
                    if self.direction != self.pos:
                        self.movements += 1
                    self.model.grid.move_agent(self, self.direction)
            else:
                self.direction = self.move(possible_steps)
                if self.direction != self.pos:
                    self.movements += 1
                self.model.grid.move_agent(self, self.direction)
        else:
            self.direction = self.gradient(possible_steps, self.drop_zone)
            if self.direction == self.drop_zone:
                self.drop_box()
            else:
                if self.direction != self.pos:
                    self.movements += 1
                self.model.grid.move_agent(self, self.direction)