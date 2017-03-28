from BalanceBot import BalanceBot

Bot = BalanceBot(10, 100, 0.25, 10, 10)
#Bot.StartBalancing()
#Bot.PosTiltErrorLarge.PrintMembershipFunction('.\\', 'Membership.png')

for TestIt in range(100):
  Bot.StartBalancing()
  #Bot.DrawBotToFile('arena' + str(TestIt) + '.png')
  #Bot.PlotFuzzySetsToFile(['TiltError' + str(TestIt) + '.png', 'RelativeWind' + str(TestIt) + '.png', 'MotorResponse' + str(TestIt) + '.png'], ['TiltError', 'Wind', 'MotorResponse'])
Bot.PlotQuantityHistories(['Position', 'Velocity', 'Acceleration', 'Tilt'])