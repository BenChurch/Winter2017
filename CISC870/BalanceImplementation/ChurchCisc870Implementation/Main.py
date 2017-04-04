# Main.py runs the simulation, generating the user specified plots as well

# Allowed sNorms: ['max']
# Allowed tNorms: ['min']
# Allowed ImplicationMethods: ['KD']

# Allowed reference frames for draw bot to file: ['Bot', 'Ground']

# Allowed fuzzy sets for plotting: ['TiltError', 'TiltIntegral', 'Wind', 'MotorResponse']

# Allowed physical quantities for plotting: ['Kinematics', 'AngularDynamics']

from BalanceBot import BalanceBot

sNorm = 'a+b-ab'
tNorm = 'min'
ImplicationMethod = 'KD'

SimulationIterations = 200

Bot = BalanceBot(1, 20, 0.25, 2, 10)

for TestIt in range(SimulationIterations  ):
  Bot.IterateSimulation(sNorm, tNorm, ImplicationMethod)
  Bot.DrawBotToFile('arena' + str(TestIt) + '.png', "Bot")
  Bot.PlotFuzzySetsToFile(['TiltError' + str(TestIt) + '.png', 'TiltIntegral' + str(TestIt) + '.png', 'MotorResponse' + str(TestIt) + '.png'], ['TiltError', 'TiltIntegral', 'MotorResponse'])
  
Bot.PlotQuantityHistories(['Kinematics', 'AngularDynamics'])