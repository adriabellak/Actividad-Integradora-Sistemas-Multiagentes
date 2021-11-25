from mesa import Model, agent
from mesa.time import RandomActivation
from mesa.space import Grid
from agent import Robot, Box, Obstacle
from mesa.datacollection import DataCollector

def get_boxes_left(model):
    return model.boxes_left

def get_moves(agent):
    if isinstance(agent, Robot):
        return agent.movements
    else:
        return 0

class BoxRobots(Model):

    """ 
    Crea un modelo para que los robots recojan cajas
    """
    def __init__(self, N, width, height, density, _max_iterations):
        self.num_agents = N
        self.grid = Grid(width,height,torus = False) 
        self.schedule = RandomActivation(self)
        self.running = True 
        self.iterations = 0
        self.max_iterations = _max_iterations
        self.boxes_left = 0
        self.initial_boxes = 0

        # Crea el borde con obstáculos
        border = [(x,y) for y in range(height) for x in range(width) if y in [0, height-1] or x in [0, width - 1]]

        for pos in border:
            obs = Obstacle(pos, self)
            self.schedule.add(obs)
            self.grid.place_agent(obs, pos)

        # Agrega Robots
        for i in range(self.num_agents):
            a = Robot(i+1000, self, (1, 1)) 
            self.schedule.add(a)
            self.grid.place_agent(a, (self.random.randint(2, width - 2) , self.random.randint(1, height - 2)))

        # Agrega el piso
        for (contents, x, y) in self.grid.coord_iter():
            # Ensucia el piso
            if not x in [0, width - 1] and not y in [0, height-1] and (x, y) != (1, 1) and self.grid.get_cell_list_contents((x, y)) == []:
                if self.random.random() < density:
                    newBox = Box((x, y), self)
                    self.grid._place_agent((x, y), newBox)
                    self.schedule.add(newBox)
                    self.boxes_left += 1
                    #print("Added dirt, now we have: ", self.dirtyCells)
        self.initial_boxes = self.boxes_left

        

        # Recolecta datos acerca de la cantidad de celdas sucias en cada iteración
        self.datacollector = DataCollector(
            model_reporters = {"Boxes left": get_boxes_left},
            agent_reporters = {"Movements": get_moves}
        )
        self.datacollector.collect(self)

    def step(self):
        '''Avanza un paso'''
        self.datacollector.collect(self)
        print("boxes left:", self.boxes_left)
        self.schedule.step()
        self.iterations += 1
        if self.iterations >= self.max_iterations or self.boxes_left <= 0:
            print("iterations:", self.iterations)
            self.running = False