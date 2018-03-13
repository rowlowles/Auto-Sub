#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect, url_for
from multiprocessing import Pipe, process
from raspipe import RasPipe
from Pi_Code import Submarine, MessageBoard


app = Flask(__name__)
rp = RasPipe(None)
#rp.input_lines.append('starting up...')
#rp.render_frame()
board = MessageBoard.MessageBoard()
sub = Submarine.Submarine(board)
@app.route('/')
def index():
    return render_template('index.html', rp=rp)

@app.route('/display', methods=['POST'])
def display():
    command = (request.form['line'].split(','))
    if command[0] == "auto" or command[0] == "manual" or command[0] == "idle":
        sub._state=command[0]
        print(command[0])

    elif command[0] == 'srv' and sub._state == "manual":
        packet = [None, None, None, None, float(command[1])]
        sub.UpdateMotorSpeed(packet)
        #print(packet)

    elif sub._state == "manual":
        com0 = float(command[0])
        com1 = float(command[1])
        left_forward = com0 <= 0
        right_forward = com1 <= 0
        packet = [abs(com0), left_forward, abs(com1), right_forward, None]
        sub.UpdateMotorSpeed(packet)
        #print(packet)

    return redirect(url_for('index'))

@app.route('/quit')
def quit():
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return "Quitting..."

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')