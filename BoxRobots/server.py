from model import BoxRobots, Robot, Box, Obstacle
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule, BarChartModule

def agent_portrayal(agent):
    if agent is None: return
    
    if isinstance(agent, Robot):
        portrayal = {"Shape": "circle",
                    "Filled": "true",
                    "Layer": 0,
                    "Color": "red",
                    "r": 1}

    if isinstance(agent, Box):
        x, y = agent.pos
        portrayal = {
            "Shape": "rect",
            "h": 1,
            "w": 1,
            "Filled": "true",
            "Layer": 1,
            "Color": "grey",
            "x": x,
            "y": y
        }

    if isinstance(agent, Obstacle):
        x, y = agent.pos
        portrayal = {
            "Shape": "rect",
            "h": 1,
            "w": 1,
            "Filled": "true",
            "Layer": 1,
            "Color" : "black",
            "x": x,
            "y": y
        }
        

    return portrayal

"""
Parámetros iniciales del modelo, el ancho y alto no se lograron hacer deslizadores porque
se requiere de valores estáticos en el CanvasGrid
"""
model_params = {
    "N": UserSettableParameter("slider", "Number of Roombas", 1, 1, 20, 1), 
    "width": 15,
    "height": 15, 
    "density" : UserSettableParameter("slider", "Box Density", 0.05, 0.01, 0.5, 0.05),
    "_max_iterations" : UserSettableParameter("slider", "Max Iterations", 1000, 10, 1000, 10)
    }

# Condiciones del gráfico
chart1 = ChartModule([{"Label": "Boxes left",
                      "Color": "Black"}],
                    )

chart2 = BarChartModule([{"Label": "Movements",
                      "Color": "Black"}],
                      scope= 'agent',
                    )

grid = CanvasGrid(agent_portrayal, 15, 15, 500, 500)
server = ModularServer(BoxRobots, [grid, chart1, chart2], "Box Robots", model_params)

server.port = "5000"
server.launch()