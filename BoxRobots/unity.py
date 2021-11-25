# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2021

from model import *
from flask import Flask, request, jsonify
from agent import *

# Size of the board:
number_robots = 10
number_boxes = 10
number_obstacles = 10
width = 28
height = 28
trafficModel = None
currentStep = 0

app = Flask("Box Robots")

# @app.route('/', methods=['POST', 'GET'])

#inicializa el Modelo en Unity
@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, trafficModel, number_agents, width, height

    if request.method == 'POST':
        #pide variables al servidor
        number_robots = int(request.form.get('NRobots'))
        number_boxes = int(request.form.get('NBoxes'))
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        max_iterations = int(request.form.get('maxMovements'))
        currentStep = 0 #se inicializa en 0 porque no ha empezado la simulación

        print(request.form)
        print(number_robots, width, height)
        # crea un objeto el model de BoxRobot
        density = number_boxes / (width*height)
        trafficModel = BoxRobots(number_robots, width, height, density, max_iterations)

        return jsonify({"message":"Parameters recieved, model initiated."})


# obtiene la posición de los agentes tipo BoxRobot
@app.route('/getRobots', methods=['GET'])
def getRobots():
    global trafficModel

    if request.method == 'GET':
        #busca la posición de los robots 
        robotPositions = [{"x": x, "y":1, "z":z} for (a, x, z) in trafficModel.grid.coord_iter() if isinstance(a, Robot)]
        # regresa esta posición a Unity
        return jsonify({'positions': robotPositions})


# obtiene la posición de los agentes tipo Box
@app.route('/getBox', methods=['GET'])
def getBox():
    global trafficModel

    if request.method == 'GET':
        #busca la posición de las cajas
        boxPositions = [{"x": x, "y":1, "z":z} for (a, x, z) in trafficModel.grid.coord_iter() if isinstance(a, Box)]
        # regresa esta posición a Unity
        return jsonify({'positions': boxPositions})


# obtiene la posición de los agentes tipo Obstacule
@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global trafficModel

    if request.method == 'GET':
        #busca la posición de los Obstaculos
        obstaclePositions = [{"x": x, "y":1, "z":z} for (a, x, z) in trafficModel.grid.coord_iter() if isinstance(a, Obstacle)]
        # regresa estas posiciones a Unity
        return jsonify({'positions': obstaclePositions})


@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, trafficModel
    if request.method == 'GET':
        if trafficModel.running == True:
            trafficModel.step()
            currentStep += 1
            return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})
        else:
            return jsonify({'message':f'Model running == False'})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)