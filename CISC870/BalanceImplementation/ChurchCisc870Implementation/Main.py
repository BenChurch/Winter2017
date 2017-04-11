# Main.py runs the simulation, generating the user specified plots as well

# Allowed sNorms: ['max', 'a+b-ab', 'min(1,a+b)']
# Allowed tNorms: ['min', 'ab', 'max(a,a+b-1)']
# Allowed ImplicationMethods: ['KD' 'RB']   Note that inference of consequent truth given partial antecdant truth and absolute rule truth does not use these methods

# Allowed reference frames for draw bot to file: ['Bot', 'Ground']

# Allowed fuzzy sets for plotting: ['TiltError', 'TiltIntegral', 'Wind', 'MotorResponse']

# Allowed physical quantities for plotting: ['Kinematics', 'AngularDynamics']

from BalanceBot import BalanceBot

sNorm = 'max'
tNorm = 'min'
ImplicationMethod = 'KD'

SimulationIterations = 100

Bot = BalanceBot(1, 20, 0.25, 2, 10)

for TestIt in range(SimulationIterations  ):
  Bot.IterateSimulation(sNorm, tNorm, ImplicationMethod)
  Bot.DrawBotToFile('arena' + str(TestIt) + '.png', "Bot")
  Bot.PlotFuzzySetsToFile(['TiltError' + str(TestIt) + '.png', 'TiltIntegral' + str(TestIt) + '.png', 'MotorResponse' + str(TestIt) + '.png'], ['TiltError', 'TiltIntegral', 'MotorResponse'])
  
Bot.PlotQuantityHistories(['Kinematics', 'AngularDynamics'])