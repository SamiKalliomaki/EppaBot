from multiprocessing import Process, Queue
from sympy import sympify, SympifyError
from botmodule import BotModule
from permissionmodule import permission_required

def do_calc(calculation, q):
	try:
		q.put(str(sympify(calculation)))
	finally:
		q.put('ERROR')

class CalcModule(BotModule):
	@permission_required('calc.calc')
	def handle_cmd_calc(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) < 1:
			raise CmdException('.calc calculation')

		calculation = ' '.join(params)
		
		q = Queue()
		p = Process(target=do_calc, args=(calculation, q))
		p.start()
		p.join(1)
		if p.is_alive():
			p.terminate()
			answer = 'TIMED OUT'
		else:
			answer = q.get()

		conn.msg_privmsg(kwargs['respond'], 'Result: {}'.format(answer))