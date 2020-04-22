import time
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import PeriodicBehaviour
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade

from multiprocessing import Pipe
import logging

import os
import csv
dirname = os.path.dirname(__file__)
CNN_DIR = os.path.join('imageClassifier', 'dnn')
CHEFF_DIR = os.path.join(dirname, '')


class ChatAgent(Agent):
    def __init__(self, jid, password, verify_security=False, pipe=None):
        super().__init__(jid, password, verify_security)
        self.pipe = pipe

    class DispatcherBehav(PeriodicBehaviour):
        async def on_start(self):
            logging.info("[ChatAgent] Starting behaviour . . .")
            # self.counter = 0

        async def on_end(self):
            self.agent.pipe.close()

        async def run(self):
            if self.agent.pipe.poll():  # Avoid blocking thread
                bot_msg = self.agent.pipe.recv() # Blocking
                logging.info("[ChatAgent] Received msg from DASI Bot: {}".format(bot_msg))
                assert type(bot_msg) == dict
                # time.sleep(1)
                t = 10
                if 'Image' in bot_msg:
                    # Notify to ImageAgent
                    msg = Message(to="dasi2020image@616.pub")
                    msg.set_metadata("performative", "request")
                    msg.body = bot_msg['Image']
                    await self.send(msg)
                elif 'CU-001' in bot_msg:
                    # Notify CheffAgent
                    msg = Message(to="dasi2020cheff@616.pub")
                    msg.set_metadata("performative", "request")
                    msg.body = 'Start cooking!'
                    await self.send(msg)

                    # Recive cheff's response
                    response = await self.receive(timeout=t)
                    # Pass response to bot - notify to user
                    if response:
                        self.agent.pipe.send(response.body)
                    else:
                        self.agent.pipe.send('Lo siento, el servidor tiene problemas. Prueba más tarde')
                elif 'CU-002' in bot_msg:
                    # Notify cheff
                    msg = Message(to="dasi2020cheff@616.pub")
                    msg.set_metadata("performative", "query_ref")
                    msg.body = bot_msg['CU-002']
                    # TODO
                    # await self.send(msg)
                    
                    # # Recive cheff's response
                    # response = await self.receive(timeout=t)
                    # # Pass response to bot - notify to user
                    # if response:
                    #     self.agent.pipe.send(response.body)
                    # else:
                    #     self.agent.pipe.send('Lo siento, el servidor tiene problemas. Prueba más tarde')
                elif 'CU-003' in bot_msg:
                    prefs = bot_msg['CU-003']
                    f = bot_msg['factor']
                    logging.info(f'[ChatAgent] Message containing {len(prefs)} preferences')
                    logging.info(f'[ChatAgent] Factor of prefs is {f}')

                    msg = Message(to="dasi2020cheff@616.pub")
                    msg.set_metadata("performative", "inform_ref")
                    v = '-10' if f == 'GuardarAlergia' else '5'
                    for i in prefs:
                        logging.info(i)
                        msg.body = str(self.agent.INGREDIENTS.index(i)) + ',' + v
                        await self.send(msg)
                        await asyncio.sleep(0.01)
                        logging.info(f"[ChatAgent * CU-003] Message sent: {msg.body}")

                else:   # bad message
                    self.kill()
            # else:
            #     await asyncio.sleep(1)
            # self.counter += 1
            # await asyncio.sleep(1)
            # if msg == '5':
            #     self.kill()

    async def setup(self):
        logging.info("ChatAgent starting . . .")
        logging.info(f"[ChatAgent] Connection mechanism: {self.pipe}")
        with open(os.path.join(CNN_DIR, 'ingredients_es.csv'), 'r') as f:
            self.INGREDIENTS = list(csv.reader(f))[0]
        
        dispatch = self.DispatcherBehav(period=1.5)
        self.add_behaviour(dispatch)

if __name__ == "__main__":

    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO)

    # creating a pipe 
    parent_conn, child_conn = Pipe() 

    # chatAgent = ChatAgent("dasi2020chat@616.pub", "123456")
    chatAgent = ChatAgent("akjncakj@616.pub", "123456", pipe=parent_conn)

    future = chatAgent.start()
    future.result()

    print("Wait until user interrupts with ctrl+C")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    chatAgent.stop()
    logging.info("Agents finished")
    quit_spade()
